"""
Semantic Memory Service
=======================
Provides long-term semantic memory using PostgreSQL + pgvector.
Stores message embeddings and retrieves the Top-K most relevant past
messages for a given user, using cosine similarity.

This complements the short-term Redis memory by providing context
from conversations that happened days or weeks ago.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.message import Message

logger = logging.getLogger(__name__)

# How many semantically similar past messages to inject into the LLM context
TOP_K_SEMANTIC = 3


async def store_message_embedding(
    db: AsyncSession,
    message_id,
    embedding: list[float],
    user_id=None,
    detected_mood: str | None = None,
    mood_confidence: float | None = None,
) -> None:
    """
    Store the embedding vector and mood metadata on an existing Message row.
    Called after the message is created in the chat endpoint.
    """
    try:
        from sqlalchemy import update
        embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        stmt = (
            update(Message)
            .where(Message.id == message_id)
            .values(
                embedding=json.dumps(embedding_list),
                user_id=user_id,
                detected_mood=detected_mood,
                mood_confidence=mood_confidence,
            )
        )
        await db.execute(stmt)
    except Exception as e:
        logger.error(f"[SemanticMemory] Failed to store embedding: {e}")


async def search_semantic_memory(
    db: AsyncSession,
    user_id,
    query_embedding: list[float],
    limit: int = TOP_K_SEMANTIC,
) -> list[dict]:
    """
    Retrieve the Top-K most semantically similar past messages for a user.

    Uses cosine similarity calculated in Python (compatible with both
    PostgreSQL with and without pgvector extension). For production
    scale (>100K messages), switch to pgvector's native <=> operator.

    Returns
    -------
    [{"role": str, "content": str, "mood": str, "score": float}, ...]
    """
    try:
        # Fetch all user messages that have embeddings
        result = await db.execute(
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.embedding.isnot(None),
                Message.role == "user",
            )
            .order_by(Message.created_at.desc())
            .limit(200)  # Cap to prevent memory issues
        )
        messages = result.scalars().all()

        if not messages:
            return []

        # Calculate cosine similarity in Python
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        scored = []
        for msg in messages:
            try:
                msg_vec = np.array(json.loads(msg.embedding))
                msg_norm = np.linalg.norm(msg_vec)
                if msg_norm == 0:
                    continue
                similarity = float(np.dot(query_vec, msg_vec) / (query_norm * msg_norm))
                scored.append({
                    "role": msg.role,
                    "content": msg.content,
                    "mood": msg.detected_mood,
                    "score": round(similarity, 4),
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                })
            except (json.JSONDecodeError, ValueError):
                continue

        # Sort by similarity descending and return top-K
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    except Exception as e:
        logger.error(f"[SemanticMemory] Search error: {e}")
        return []
