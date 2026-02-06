"""FastAPI application – API endpoints for the Virtual Representatives system."""

import logging

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db, init_db
from backend.document_processor import extract_text, store_document
from backend.llm import chat as llm_chat
from shared.models import Document
from shared.personas import list_departments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Virtual Department Representatives")

# Allow the Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Backend started")


# --------------- Pydantic request schemas ---------------

class ChatRequest(BaseModel):
    department: str
    message: str
    history: list[dict] | None = None


# --------------- Endpoints ---------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/departments")
def get_departments():
    """Return all available department personas."""
    return list_departments()


@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    """Return all uploaded documents."""
    docs = db.query(Document).order_by(Document.upload_date.desc()).all()
    return [d.to_dict() for d in docs]


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted"}


@app.post("/upload/document")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse a text/PDF file, storing it in the knowledge base."""
    allowed_extensions = (".txt", ".md", ".pdf")
    if not file.filename or not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    content_bytes = await file.read()
    try:
        text = extract_text(file.filename, content_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    doc = store_document(db, title=file.filename, content=text)
    return doc.to_dict()


@app.post("/chat")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """Query a department representative with a message."""
    try:
        reply = llm_chat(req.department, req.message, db, history=req.history)
        return {"department": req.department, "reply": reply}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
