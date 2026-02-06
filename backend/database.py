"""SQLite database connection and initialization."""

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.models import Base

logger = logging.getLogger(__name__)

# Resolve DB path relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "knowledge.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables if they don't exist yet."""
    os.makedirs(DB_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", DB_PATH)


def get_db():
    """Yield a database session (FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
