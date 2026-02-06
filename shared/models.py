"""SQLAlchemy database models for the Virtual Representatives system."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Document(Base):
    """Stores uploaded documents (meeting notes, PDFs, etc.) as knowledge base entries."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    tags = Column(Text, default="[]")  # JSON string of tags
    extra_metadata = Column("metadata", Text, default="{}")  # JSON string of extra metadata

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "tags": self.tags,
            "metadata": self.extra_metadata,
        }
