"""SQLAlchemy database models for the Virtual Representatives system."""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
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


class User(Base):
    """Stores Google-authenticated users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=False)
    picture_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture_url": self.picture_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class ConversationMessage(Base):
    """Persists chat messages per user per department."""

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }


class DashboardSnapshot(Base):
    """Caches a daily LLM-generated dashboard per department."""

    __tablename__ = "dashboard_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Markdown content
    charts_json = Column(Text, nullable=False, default="[]")  # JSON array of chart data
    generated_date = Column(Date, nullable=False, default=date.today)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "department": self.department,
            "content": self.content,
            "charts_json": self.charts_json,
            "generated_date": self.generated_date.isoformat(),
            "generated_at": self.generated_at.isoformat(),
        }
