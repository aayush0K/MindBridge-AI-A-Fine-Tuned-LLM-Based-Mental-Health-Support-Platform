import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Float, Text, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_crisis: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Phase 7/9: Mood detection & Semantic memory fields ────────────────────
    detected_mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mood_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-serialized vector
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
