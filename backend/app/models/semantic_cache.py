"""
Semantic Cache Model — Stores reusable AI responses and their MiniLM-L6-v2 embeddings.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Float, Integer, Text, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

try:
    from pgvector.sqlalchemy import Vector
    EmbeddingColumnType = Vector(384)
except ImportError:
    EmbeddingColumnType = Text  # Fallback for environments without pgvector lib


class SemanticCache(Base):
    __tablename__ = "semantic_cache"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 384-dimensional dense vector for sentence-transformers/all-MiniLM-L6-v2
    embedding: Mapped[list[float] | str] = mapped_column(EmbeddingColumnType, nullable=False)
    
    detected_mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    similarity_threshold: Mapped[float] = mapped_column(Float, default=0.90)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
