import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Uuid, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WellnessReport(Base):
    __tablename__ = "wellness_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    report_type: Mapped[str] = mapped_column(String(50), default="30_day_summary")
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Structured report content
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_topics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    mood_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
