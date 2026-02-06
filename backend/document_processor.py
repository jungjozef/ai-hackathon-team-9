"""Document parsing and storage for uploaded files."""

import json
import logging
import os

from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from shared.models import Document

logger = logging.getLogger(__name__)


def extract_text(filename: str, content_bytes: bytes) -> str:
    """Extract plain text from a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()

    if ext in (".txt", ".md"):
        return content_bytes.decode("utf-8", errors="replace")

    if ext == ".pdf":
        return _extract_pdf_text(content_bytes)

    raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf_text(content_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    import io

    reader = PdfReader(io.BytesIO(content_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def store_document(
    db: Session,
    title: str,
    content: str,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> Document:
    """Store a parsed document in the database and return it."""
    doc = Document(
        title=title,
        content=content,
        tags=json.dumps(tags or []),
        extra_metadata=json.dumps(metadata or {}),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info("Stored document id=%s title=%s", doc.id, doc.title)
    return doc
