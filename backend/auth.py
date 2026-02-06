"""Google OAuth + JWT authentication for the Virtual Representatives API."""

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google_auth_oauthlib.flow import Flow
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.models import User

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

# ---- Configuration (loaded from environment) ----

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-to-a-random-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))

REDIRECT_URI = "http://localhost:8000/auth/google/callback"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# FastAPI security scheme for extracting Bearer tokens
bearer_scheme = HTTPBearer(auto_error=False)


# ---- Google OAuth helpers ----


def get_google_oauth_flow() -> Flow:
    """Build a Google OAuth2 Flow from env-var credentials (no JSON file needed)."""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


# ---- JWT helpers ----


def create_jwt_token(user: User) -> str:
    """Create a signed JWT containing user id and email."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Decode and validate a JWT, returning its payload or raising."""
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


# ---- User helpers ----


def get_or_create_user(
    db: Session, google_id: str, email: str, name: str, picture_url: str | None
) -> User:
    """Find an existing user by google_id or create a new one."""
    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        user.last_login = datetime.now(timezone.utc)
        user.name = name
        user.picture_url = picture_url
        db.commit()
        db.refresh(user)
        return user

    user = User(
        email=email,
        name=name,
        google_id=google_id,
        picture_url=picture_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---- FastAPI dependency ----


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency – extracts JWT from Authorization header and returns the User, or raises 401."""
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = verify_jwt_token(creds.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user
