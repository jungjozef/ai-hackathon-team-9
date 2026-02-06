"""SQLite database connection and initialization."""

import logging
import os

from sqlalchemy import create_engine, inspect, text
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


def _run_migrations():
    """Add any columns that are missing from existing tables."""
    inspector = inspect(engine)
    migrations = [
        ("dashboard_snapshots", "charts_json", "TEXT NOT NULL DEFAULT '[]'"),
    ]
    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if table in inspector.get_table_names():
                existing = [c["name"] for c in inspector.get_columns(table)]
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()
                    logger.info("Migrated: added %s.%s", table, column)


def init_db():
    """Create all tables if they don't exist yet, then run lightweight migrations."""
    os.makedirs(DB_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    logger.info("Database initialized at %s", DB_PATH)


def get_db():
    """Yield a database session (FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
