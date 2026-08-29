import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, CheckConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False)
    mood_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── Phase 7/8: Automated mood detection fields ────────────────────────────
    auto_detected: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    raw_label: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint("mood_score BETWEEN 1 AND 10", name="ck_mood_score_range"),
    )
