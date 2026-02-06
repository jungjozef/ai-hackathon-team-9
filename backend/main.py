"""FastAPI application – API endpoints for the Virtual Representatives system."""

import logging
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import (
    create_jwt_token,
    get_current_user,
    get_google_oauth_flow,
    get_or_create_user,
)
from backend.database import get_db, init_db
from backend.document_processor import extract_text, store_document
from backend.llm import chat as llm_chat
from shared.models import Document, User
from shared.personas import list_departments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Virtual Department Representatives",
    description="API for querying department-specific AI representatives backed by an uploaded knowledge base.",
    version="1.0.0",
    docs_url="/apidocs",
)

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


# --------------- Public endpoints ---------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/departments")
def get_departments():
    """Return all available department personas."""
    return list_departments()


# --------------- Auth endpoints ---------------

@app.get("/auth/google/login")
def google_login():
    """Return the Google OAuth authorization URL."""
    flow = get_google_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )
    return {"authorization_url": auth_url}


@app.get("/auth/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle the OAuth redirect from Google, create/update user, and redirect to Streamlit with a JWT."""
    flow = get_google_oauth_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials
    # Use the id_token to get user info without an extra API call
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport.requests import Request as GoogleRequest

    id_info = google_id_token.verify_oauth2_token(
        credentials.id_token,
        GoogleRequest(),
        flow.client_config["client_id"],
    )

    user = get_or_create_user(
        db,
        google_id=id_info["sub"],
        email=id_info["email"],
        name=id_info.get("name", id_info["email"]),
        picture_url=id_info.get("picture"),
    )

    token = create_jwt_token(user)
    # Redirect back to Streamlit with the JWT as a query parameter
    redirect_url = f"http://localhost:8501/?{urlencode({'token': token})}"
    return RedirectResponse(url=redirect_url)


@app.get("/auth/me")
def auth_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's info."""
    return current_user.to_dict()


@app.post("/auth/logout")
def auth_logout():
    """Placeholder logout – the client simply discards the token."""
    return {"detail": "Logged out (discard the token client-side)"}


# --------------- Protected endpoints ---------------

@app.get("/documents")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return all uploaded documents."""
    docs = db.query(Document).order_by(Document.upload_date.desc()).all()
    return [d.to_dict() for d in docs]


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted"}


@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query a department representative with a message."""
    try:
        reply = llm_chat(req.department, req.message, db, history=req.history)
        return {"department": req.department, "reply": reply}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
