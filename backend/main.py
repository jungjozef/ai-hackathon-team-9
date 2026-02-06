"""FastAPI application – API endpoints for the Virtual Representatives system."""

import logging
import os
from datetime import date, datetime
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth import (
    create_jwt_token,
    get_current_user,
    get_google_oauth_flow,
    get_or_create_user,
)
from backend.database import get_db, init_db
from backend.document_processor import extract_text, store_document
from backend.llm import chat as llm_chat, generate_dashboard, generate_dashboard_charts
from shared.models import ConversationMessage, DashboardSnapshot, Document, User
from shared.personas import list_departments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------- OpenAPI tag metadata ---------------

tags_metadata = [
    {
        "name": "Health",
        "description": "Server health check.",
    },
    {
        "name": "Auth",
        "description": "Google OAuth 2.0 login flow and session management. "
        "Use `/auth/google/login` to start the flow, Google redirects to `/auth/google/callback`, "
        "and a JWT is returned to the Streamlit frontend.",
    },
    {
        "name": "Departments",
        "description": "List the available department personas (Engineering, Delivery, Admin, Sales, C-level, Marketing).",
    },
    {
        "name": "Documents",
        "description": "Upload, list, and delete knowledge-base documents (`.txt`, `.md`, `.pdf`). "
        "All endpoints require a valid Bearer token.",
    },
    {
        "name": "Dashboard",
        "description": "LLM-generated daily dashboards with charts for each department. "
        "Dashboards are cached once per day; use the regenerate endpoint to force a refresh. "
        "All endpoints require a valid Bearer token.",
    },
    {
        "name": "Chat",
        "description": "Converse with a department representative powered by Ollama. "
        "Conversation history is persisted per user per department. "
        "All endpoints require a valid Bearer token.",
    },
]

app = FastAPI(
    title="Virtual Department Representatives",
    description=(
        "REST API for the **Virtual Department Representatives** system.\n\n"
        "The API provides:\n"
        "- **Google SSO** authentication (OAuth 2.0 + JWT)\n"
        "- **Knowledge-base** document management (upload / list / delete)\n"
        "- **Department dashboards** with auto-generated charts (cached daily)\n"
        "- **Chat** with AI-powered department representatives via Ollama\n\n"
        "### Authentication\n"
        "Most endpoints require a **Bearer token** in the `Authorization` header. "
        "Obtain one by completing the Google OAuth flow starting at `/auth/google/login`."
    ),
    version="1.0.0",
    docs_url="/apidocs",
    openapi_tags=tags_metadata,
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


# --------------- Pydantic schemas ---------------

class ChatRequest(BaseModel):
    """Payload for sending a message to a department representative."""
    department: str = Field(..., description="Department name (e.g. Engineering, Sales, C-level)")
    message: str = Field(..., description="The user's message / question")
    history: list[dict] | None = Field(None, description="Prior conversation turns for context")


class ChatResponse(BaseModel):
    """Response from a department representative."""
    department: str
    reply: str


class ChatMessageOut(BaseModel):
    """A single persisted chat message."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class DocumentOut(BaseModel):
    """A knowledge-base document."""
    id: int
    title: str
    content: str
    upload_date: str | None
    tags: str
    metadata: str


class DepartmentOut(BaseModel):
    """A department persona summary."""
    name: str
    icon: str
    description: str


class DashboardOut(BaseModel):
    """A daily dashboard snapshot for a department."""
    department: str
    content: str = Field(..., description="Markdown-formatted dashboard content")
    charts_json: str = Field(..., description="JSON array of chart data objects")
    generated_date: str
    generated_at: str


class UserOut(BaseModel):
    """Authenticated user profile."""
    id: int
    email: str
    name: str
    picture_url: str | None
    created_at: str | None
    last_login: str | None


class AuthUrlOut(BaseModel):
    """Google OAuth authorization URL."""
    authorization_url: str


class DetailOut(BaseModel):
    """Generic detail / status message."""
    detail: str


class HealthOut(BaseModel):
    """Health check response."""
    status: str


# --------------- Public endpoints ---------------

@app.get(
    "/health",
    tags=["Health"],
    response_model=HealthOut,
    summary="Health check",
    description="Returns `ok` if the backend is running.",
)
def health():
    return {"status": "ok"}


@app.get(
    "/departments",
    tags=["Departments"],
    response_model=list[DepartmentOut],
    summary="List departments",
    description="Returns all available department personas with their name, icon, and description.",
)
def get_departments():
    return list_departments()


# --------------- Auth endpoints ---------------

@app.get(
    "/auth/google/login",
    tags=["Auth"],
    response_model=AuthUrlOut,
    summary="Start Google OAuth flow",
    description="Returns a Google OAuth authorization URL. Redirect the user to this URL to begin sign-in.",
)
def google_login():
    flow = get_google_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )
    return {"authorization_url": auth_url}


@app.get(
    "/auth/google/callback",
    tags=["Auth"],
    summary="Google OAuth callback",
    description="Handles the redirect from Google after user consent. "
    "Exchanges the authorization code for tokens, creates or updates the user, "
    "generates a JWT, and redirects to the Streamlit frontend with `?token=<jwt>`.",
    responses={302: {"description": "Redirect to Streamlit with JWT"}},
)
def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    db: Session = Depends(get_db),
):
    flow = get_google_oauth_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials
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
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    redirect_url = f"{frontend_url}/?{urlencode({'token': token})}"
    return RedirectResponse(url=redirect_url)


@app.get(
    "/auth/me",
    tags=["Auth"],
    response_model=UserOut,
    summary="Get current user",
    description="Returns the profile of the currently authenticated user. Use this to validate a JWT.",
    responses={401: {"description": "Not authenticated or token expired"}},
)
def auth_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


@app.post(
    "/auth/logout",
    tags=["Auth"],
    response_model=DetailOut,
    summary="Logout",
    description="Placeholder endpoint. The client should discard the JWT to log out.",
)
def auth_logout():
    return {"detail": "Logged out (discard the token client-side)"}


# --------------- Document endpoints ---------------

@app.get(
    "/documents",
    tags=["Documents"],
    response_model=list[DocumentOut],
    summary="List documents",
    description="Returns all uploaded knowledge-base documents, newest first.",
    responses={401: {"description": "Not authenticated"}},
)
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).order_by(Document.upload_date.desc()).all()
    return [d.to_dict() for d in docs]


@app.delete(
    "/documents/{doc_id}",
    tags=["Documents"],
    response_model=DetailOut,
    summary="Delete a document",
    description="Permanently removes a document from the knowledge base by its ID.",
    responses={401: {"description": "Not authenticated"}, 404: {"description": "Document not found"}},
)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"detail": "Document deleted"}


@app.post(
    "/upload/document",
    tags=["Documents"],
    response_model=DocumentOut,
    summary="Upload a document",
    description="Upload a `.txt`, `.md`, or `.pdf` file. The content is extracted and stored in the knowledge base.",
    responses={400: {"description": "Unsupported file type or parse error"}, 401: {"description": "Not authenticated"}},
)
async def upload_document(
    file: UploadFile = File(..., description="Text, Markdown, or PDF file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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


# --------------- Dashboard endpoints ---------------

@app.get(
    "/dashboard/{department}",
    tags=["Dashboard"],
    response_model=DashboardOut,
    summary="Get department dashboard",
    description="Returns today's cached dashboard for the given department. "
    "If no dashboard has been generated today, it is created on the fly (may take up to 60 seconds). "
    "The response includes Markdown content and a JSON array of chart data.",
    responses={401: {"description": "Not authenticated"}, 503: {"description": "LLM unavailable"}},
)
def get_dashboard(
    department: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    snapshot = (
        db.query(DashboardSnapshot)
        .filter(
            DashboardSnapshot.department == department,
            DashboardSnapshot.generated_date == today,
        )
        .first()
    )

    if snapshot:
        return snapshot.to_dict()

    try:
        content = generate_dashboard(department, db)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=503, detail=str(e))

    charts_json = generate_dashboard_charts(department, db)

    snapshot = DashboardSnapshot(
        department=department, content=content, charts_json=charts_json, generated_date=today,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot.to_dict()


@app.post(
    "/dashboard/{department}/regenerate",
    tags=["Dashboard"],
    response_model=DashboardOut,
    summary="Regenerate department dashboard",
    description="Force-regenerates today's dashboard for the given department, "
    "replacing any previously cached version. Useful after uploading new documents.",
    responses={401: {"description": "Not authenticated"}, 503: {"description": "LLM unavailable"}},
)
def regenerate_dashboard(
    department: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = generate_dashboard(department, db)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=503, detail=str(e))

    charts_json = generate_dashboard_charts(department, db)

    today = date.today()
    existing = (
        db.query(DashboardSnapshot)
        .filter(
            DashboardSnapshot.department == department,
            DashboardSnapshot.generated_date == today,
        )
        .first()
    )
    if existing:
        existing.content = content
        existing.charts_json = charts_json
        existing.generated_at = datetime.utcnow()
    else:
        existing = DashboardSnapshot(
            department=department, content=content, charts_json=charts_json, generated_date=today,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing.to_dict()


# --------------- Chat endpoints ---------------

@app.post(
    "/chat",
    tags=["Chat"],
    response_model=ChatResponse,
    summary="Send a message to a representative",
    description="Sends a user message to the specified department's AI representative. "
    "The message and reply are persisted to the conversation history. "
    "Prior conversation turns can be passed in `history` for context.",
    responses={401: {"description": "Not authenticated"}, 503: {"description": "LLM unavailable"}},
)
def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        reply = llm_chat(req.department, req.message, db, history=req.history)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    db.add(ConversationMessage(user_id=current_user.id, department=req.department, role="user", content=req.message))
    db.add(ConversationMessage(user_id=current_user.id, department=req.department, role="assistant", content=reply))
    db.commit()

    return {"department": req.department, "reply": reply}


@app.get(
    "/chat/history",
    tags=["Chat"],
    response_model=list[ChatMessageOut],
    summary="Get conversation history",
    description="Returns the full conversation history for the current user and department, ordered oldest first.",
    responses={401: {"description": "Not authenticated"}},
)
def get_chat_history(
    department: str = Query(..., description="Department name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.user_id == current_user.id,
            ConversationMessage.department == department,
        )
        .order_by(ConversationMessage.created_at.asc())
        .all()
    )
    return [m.to_dict() for m in messages]


@app.delete(
    "/chat/history",
    tags=["Chat"],
    response_model=DetailOut,
    summary="Clear conversation history",
    description="Deletes all conversation messages for the current user and department.",
    responses={401: {"description": "Not authenticated"}},
)
def delete_chat_history(
    department: str = Query(..., description="Department name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(ConversationMessage).filter(
        ConversationMessage.user_id == current_user.id,
        ConversationMessage.department == department,
    ).delete()
    db.commit()
    return {"detail": f"History cleared for {department}"}
