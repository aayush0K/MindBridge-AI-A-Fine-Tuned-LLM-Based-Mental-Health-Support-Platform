"""
Journal Model — Private reflections and journal entries.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Uuid, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Reflection")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood_tag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
