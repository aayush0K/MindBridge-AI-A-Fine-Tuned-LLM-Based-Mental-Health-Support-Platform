"""
Semantic Cache Service
======================
Handles semantic caching of generic reusable AI responses in PostgreSQL
using pgvector and MiniLM-L6-v2 384-dimensional embeddings.

Responsibilities:
  - Cache lookup with configurable cosine similarity threshold (default 0.90)
  - Mood and emotional context compatibility filtering
  - TTL expiration management (default 30 days)
  - Duplicate vector prevention
  - Integration with latency and hit/miss metrics tracking
  - Resilient error handling (never blocks or crashes the chat pipeline)
"""

from __future__ import annotations

import time
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text, and_

from app.models.semantic_cache import SemanticCache
from app.config import settings
from app.safety.pii_filter import is_reusable_guidance, is_mood_compatible
from app.services.metrics_service import cache_metrics

logger = logging.getLogger(__name__)


class SemanticCacheService:
    """Service managing semantic lookup and caching of AI responses in PostgreSQL."""

    def __init__(self):
        self.enabled: bool = getattr(settings, "SEMANTIC_CACHE_ENABLED", True)
        self.threshold: float = getattr(settings, "SEMANTIC_CACHE_THRESHOLD", 0.90)
        self.ttl_days: int = getattr(settings, "SEMANTIC_CACHE_TTL_DAYS", 30)

    async def lookup(
        self,
        db: AsyncSession,
        query_text: str,
        query_vector: list[float] | np.ndarray,
        current_mood: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a semantically similar, mood-compatible cached response.

        Returns
        -------
        Dict with response, similarity, and metadata on HIT, or None on MISS.
        """
        if not self.enabled or db is None:
            return None

        start_time = time.perf_counter()
        query_vec_list = (
            query_vector.tolist() if isinstance(query_vector, np.ndarray) else list(query_vector)
        )
        now = datetime.now(timezone.utc)

        try:
            # Query all active and unexpired cache candidates
            stmt = (
                select(SemanticCache)
                .where(
                    and_(
                        SemanticCache.is_active == True,
                        SemanticCache.expires_at > now,
                    )
                )
                .limit(200)
            )
            result = await db.execute(stmt)
            candidates: List[SemanticCache] = result.scalars().all()

            if not candidates:
                lookup_ms = (time.perf_counter() - start_time) * 1000.0
                cache_metrics.record_miss(lookup_ms)
                return None

            q_vec = np.array(query_vec_list, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                lookup_ms = (time.perf_counter() - start_time) * 1000.0
                cache_metrics.record_miss(lookup_ms)
                return None

            best_match: Optional[SemanticCache] = None
            best_similarity: float = -1.0

            for entry in candidates:
                # Handle vector format (pgvector array, list, or JSON string)
                if isinstance(entry.embedding, str):
                    try:
                        emb = np.array(json.loads(entry.embedding), dtype=np.float32)
                    except Exception:
                        continue
                elif isinstance(entry.embedding, (list, np.ndarray)):
                    emb = np.array(entry.embedding, dtype=np.float32)
                else:
                    # pgvector Vector object
                    emb = np.array(list(entry.embedding), dtype=np.float32)

                emb_norm = np.linalg.norm(emb)
                if emb_norm == 0:
                    continue

                cosine_sim = float(np.dot(q_vec, emb) / (q_norm * emb_norm))

                # Must exceed threshold
                effective_threshold = max(self.threshold, entry.similarity_threshold)
                if cosine_sim >= effective_threshold and cosine_sim > best_similarity:
                    # Check mood / emotional context compatibility
                    if is_mood_compatible(entry.detected_mood, current_mood):
                        best_similarity = cosine_sim
                        best_match = entry

            lookup_ms = (time.perf_counter() - start_time) * 1000.0

            if best_match is not None:
                # Update hit stats
                try:
                    await db.execute(
                        update(SemanticCache)
                        .where(SemanticCache.id == best_match.id)
                        .values(
                            hit_count=SemanticCache.hit_count + 1,
                            last_accessed_at=now,
                        )
                    )
                    await db.flush()
                except Exception as e:
                    logger.warning(f"[SemanticCache] Failed to update hit_count: {e}")

                cache_metrics.record_hit(best_similarity, lookup_ms)
                return {
                    "response": best_match.response_text,
                    "similarity": round(best_similarity, 4),
                    "cached_query": best_match.query_text,
                    "detected_mood": best_match.detected_mood,
                    "category": best_match.category,
                    "hit_count": best_match.hit_count + 1,
                    "cached_id": str(best_match.id),
                }

            cache_metrics.record_miss(lookup_ms)
            return None

        except Exception as exc:
            lookup_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"[SemanticCache] Error during cache lookup (graceful fallback): {exc}")
            cache_metrics.record_miss(lookup_ms)
            return None

    async def store(
        self,
        db: AsyncSession,
        query_text: str,
        query_vector: list[float] | np.ndarray,
        response_text: str,
        detected_mood: Optional[str] = None,
        category: Optional[str] = None,
    ) -> bool:
        """
        Validate and store a generic, reusable AI response in the semantic cache.

        Returns
        -------
        True if successfully stored, False otherwise.
        """
        if not self.enabled or db is None:
            return False

        try:
            # 1. Privacy & Safety Validation
            if not is_reusable_guidance(query_text, response_text):
                return False

            now = datetime.now(timezone.utc)
            query_vec_list = (
                query_vector.tolist() if isinstance(query_vector, np.ndarray) else list(query_vector)
            )
            q_vec = np.array(query_vec_list, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)

            # 2. Duplicate Prevention: Check if very close vector (>0.98 similarity) already exists
            existing_res = await db.execute(
                select(SemanticCache).where(
                    and_(
                        SemanticCache.is_active == True,
                        SemanticCache.expires_at > now,
                    )
                ).limit(50)
            )
            existing_entries = existing_res.scalars().all()

            for entry in existing_entries:
                if entry.query_text.strip().lower() == query_text.strip().lower():
                    logger.debug(f"[SemanticCache] Exact query match exists; skipping duplicate insert.")
                    return False

                if q_norm > 0:
                    try:
                        emb = np.array(list(entry.embedding), dtype=np.float32)
                        emb_norm = np.linalg.norm(emb)
                        if emb_norm > 0:
                            sim = float(np.dot(q_vec, emb) / (q_norm * emb_norm))
                            if sim >= 0.98:
                                logger.debug(
                                    f"[SemanticCache] High similarity entry ({sim:.3f}) already in cache; skipping insert."
                                )
                                return False
                    except Exception:
                        pass

            # 3. Create and persist new cache row
            expires_at = now + timedelta(days=self.ttl_days)
            cache_row = SemanticCache(
                query_text=query_text.strip(),
                response_text=response_text.strip(),
                embedding=query_vec_list,
                detected_mood=detected_mood,
                category=category,
                similarity_threshold=self.threshold,
                hit_count=0,
                created_at=now,
                last_accessed_at=now,
                expires_at=expires_at,
                is_active=True,
            )
            db.add(cache_row)
            await db.flush()
            logger.info(
                f"[SemanticCache] Cached new guidance for: '{query_text[:40]}...' (TTL: {self.ttl_days}d)"
            )
            return True

        except Exception as exc:
            logger.error(f"[SemanticCache] Failed to store cache entry: {exc}")
            return False


# Global singleton
cache_service = SemanticCacheService()
