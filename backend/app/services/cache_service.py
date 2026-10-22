"""
Semantic Cache Service (Ultra-Fast Two-Tier Architecture)
==========================================================
Tier 1: L1 In-Memory Hot Cache (0.005s lookup, 0 network hops)
Tier 2: L2 PostgreSQL pgvector Persistence (Neon Cloud DB)

Features:
  - Sub-millisecond in-memory vector cosine similarity
  - Mood & context safety compatibility
  - Persistent fallback and write-through to PostgreSQL
  - Graceful degradation (never blocks or crashes chat flow)
"""

from __future__ import annotations

import time
import json
import logging
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.semantic_cache import SemanticCache
from app.config import settings
from app.safety.pii_filter import is_reusable_guidance, is_mood_compatible
from app.services.metrics_service import cache_metrics

logger = logging.getLogger(__name__)


class FastMemoryCacheEntry:
    __slots__ = ("id", "query_text", "response_text", "embedding", "norm", "detected_mood", "category", "threshold", "expires_at", "hit_count")

    def __init__(
        self,
        id_str: str,
        query_text: str,
        response_text: str,
        embedding: np.ndarray,
        detected_mood: Optional[str],
        category: Optional[str],
        threshold: float,
        expires_at: datetime,
        hit_count: int = 0,
    ):
        self.id = id_str
        self.query_text = query_text
        self.response_text = response_text
        self.embedding = embedding
        self.norm = float(np.linalg.norm(embedding))
        self.detected_mood = detected_mood
        self.category = category
        self.threshold = threshold
        self.expires_at = expires_at
        self.hit_count = hit_count


class SemanticCacheService:
    """Two-tier semantic cache service for instant AI response retrieval."""

    def __init__(self):
        self.enabled: bool = getattr(settings, "SEMANTIC_CACHE_ENABLED", True)
        self.threshold: float = getattr(settings, "SEMANTIC_CACHE_THRESHOLD", 0.82)
        self.ttl_days: int = getattr(settings, "SEMANTIC_CACHE_TTL_DAYS", 30)
        self.max_l1_items: int = 300
        # In-memory LRU storage: id -> FastMemoryCacheEntry
        self._l1_cache: OrderedDict[str, FastMemoryCacheEntry] = OrderedDict()
        self._l1_warmed: bool = False

    def _add_to_l1(self, entry: FastMemoryCacheEntry):
        """Add or refresh an entry in L1 memory with LRU eviction."""
        if entry.id in self._l1_cache:
            self._l1_cache.move_to_end(entry.id)
            self._l1_cache[entry.id] = entry
            return

        if len(self._l1_cache) >= self.max_l1_items:
            self._l1_cache.popitem(last=False)  # pop oldest

        self._l1_cache[entry.id] = entry

    async def _warm_l1_from_db(self, db: AsyncSession):
        """Preload the most recent active cache entries into L1 memory once on startup."""
        if self._l1_warmed or db is None:
            return
        try:
            now = datetime.now(timezone.utc)
            stmt = (
                select(SemanticCache)
                .where(
                    and_(
                        SemanticCache.is_active == True,
                        SemanticCache.expires_at > now,
                    )
                )
                .order_by(SemanticCache.last_accessed_at.desc())
                .limit(self.max_l1_items)
            )
            result = await db.execute(stmt)
            rows = result.scalars().all()
            for r in rows:
                if isinstance(r.embedding, str):
                    emb = np.array(json.loads(r.embedding), dtype=np.float32)
                else:
                    emb = np.array(list(r.embedding), dtype=np.float32)

                entry = FastMemoryCacheEntry(
                    id_str=str(r.id),
                    query_text=r.query_text,
                    response_text=r.response_text,
                    embedding=emb,
                    detected_mood=r.detected_mood,
                    category=r.category,
                    threshold=r.similarity_threshold,
                    expires_at=r.expires_at,
                    hit_count=r.hit_count,
                )
                self._add_to_l1(entry)

            self._l1_warmed = True
            logger.info(f"[SemanticCache] L1 In-Memory Cache warmed with {len(rows)} entries from DB.")
        except Exception as e:
            logger.warning(f"[SemanticCache] L1 pre-warm skipped/failed: {e}")

    async def lookup(
        self,
        db: AsyncSession,
        query_text: str,
        query_vector: list[float] | np.ndarray,
        current_mood: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Ultra-fast two-tier cache lookup:
          1. Scans L1 memory (0.002 - 0.005s)
          2. If L1 misses, queries L2 database and populates L1
        """
        if not self.enabled:
            return None

        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        # Lazy warm L1 on first query if needed
        if not self._l1_warmed and db is not None:
            await self._warm_l1_from_db(db)

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = float(np.linalg.norm(q_vec))
        if q_norm == 0:
            return None

        best_entry: Optional[FastMemoryCacheEntry] = None
        best_sim: float = -1.0

        # ── Step 1: Check L1 In-Memory Cache (Blazing Fast) ────────────────
        for entry in self._l1_cache.values():
            if entry.expires_at <= now:
                continue

            if entry.norm == 0:
                continue

            # Dot product divided by norms
            sim = float(np.dot(q_vec, entry.embedding) / (q_norm * entry.norm))
            eff_threshold = max(self.threshold, entry.threshold)

            if sim >= eff_threshold and sim > best_sim:
                if is_mood_compatible(entry.detected_mood, current_mood):
                    best_sim = sim
                    best_entry = entry

        if best_entry is not None:
            lookup_ms = (time.perf_counter() - start_time) * 1000.0
            best_entry.hit_count += 1
            self._l1_cache.move_to_end(best_entry.id)
            cache_metrics.record_hit(best_sim, lookup_ms)
            logger.info(
                f"[SemanticCache] L1 Memory Cache HIT! (sim={best_sim:.4f}, latency={lookup_ms:.2f}ms)"
            )

            # Fire-and-forget hit update in DB
            if db is not None:
                try:
                    await db.execute(
                        update(SemanticCache)
                        .where(SemanticCache.id == best_entry.id)
                        .values(
                            hit_count=best_entry.hit_count,
                            last_accessed_at=now,
                        )
                    )
                    await db.flush()
                except Exception:
                    pass

            return {
                "response": best_entry.response_text,
                "similarity": round(best_sim, 4),
                "cached_query": best_entry.query_text,
                "detected_mood": best_entry.detected_mood,
                "category": best_entry.category,
                "hit_count": best_entry.hit_count,
                "cached_id": best_entry.id,
            }

        # ── Step 2: Fallback to L2 Database (if L1 didn't have it) ─────────
        if db is not None:
            try:
                stmt = (
                    select(SemanticCache)
                    .where(
                        and_(
                            SemanticCache.is_active == True,
                            SemanticCache.expires_at > now,
                        )
                    )
                    .limit(100)
                )
                res = await db.execute(stmt)
                db_candidates = res.scalars().all()

                for r in db_candidates:
                    if isinstance(r.embedding, str):
                        emb = np.array(json.loads(r.embedding), dtype=np.float32)
                    else:
                        emb = np.array(list(r.embedding), dtype=np.float32)

                    emb_norm = float(np.linalg.norm(emb))
                    if emb_norm == 0:
                        continue

                    sim = float(np.dot(q_vec, emb) / (q_norm * emb_norm))
                    eff_threshold = max(self.threshold, r.similarity_threshold)

                    if sim >= eff_threshold and sim > best_sim:
                        if is_mood_compatible(r.detected_mood, current_mood):
                            best_sim = sim
                            # Populate to L1
                            mem_entry = FastMemoryCacheEntry(
                                id_str=str(r.id),
                                query_text=r.query_text,
                                response_text=r.response_text,
                                embedding=emb,
                                detected_mood=r.detected_mood,
                                category=r.category,
                                threshold=r.similarity_threshold,
                                expires_at=r.expires_at,
                                hit_count=r.hit_count + 1,
                            )
                            self._add_to_l1(mem_entry)
                            best_entry = mem_entry

                if best_entry is not None:
                    lookup_ms = (time.perf_counter() - start_time) * 1000.0
                    cache_metrics.record_hit(best_sim, lookup_ms)
                    logger.info(f"[SemanticCache] L2 DB Cache HIT! (sim={best_sim:.4f})")
                    return {
                        "response": best_entry.response_text,
                        "similarity": round(best_sim, 4),
                        "cached_query": best_entry.query_text,
                        "detected_mood": best_entry.detected_mood,
                        "category": best_entry.category,
                        "hit_count": best_entry.hit_count,
                        "cached_id": best_entry.id,
                    }
            except Exception as e:
                logger.warning(f"[SemanticCache] L2 DB lookup error: {e}")

        lookup_ms = (time.perf_counter() - start_time) * 1000.0
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
        """Store guidance in both L1 memory cache and L2 PostgreSQL."""
        if not self.enabled or db is None:
            return False

        try:
            if not is_reusable_guidance(query_text, response_text):
                return False

            now = datetime.now(timezone.utc)
            query_vec_list = (
                query_vector.tolist() if isinstance(query_vector, np.ndarray) else list(query_vector)
            )
            q_vec = np.array(query_vec_list, dtype=np.float32)
            q_norm = float(np.linalg.norm(q_vec))

            # Duplicate check in memory first (ultra-fast)
            clean_q = query_text.strip().lower()
            for entry in self._l1_cache.values():
                if entry.query_text.strip().lower() == clean_q:
                    return False
                if q_norm > 0 and entry.norm > 0:
                    sim = float(np.dot(q_vec, entry.embedding) / (q_norm * entry.norm))
                    if sim >= 0.98:
                        return False

            # Persist to L2 PostgreSQL
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

            # Add to L1 memory cache immediately
            mem_entry = FastMemoryCacheEntry(
                id_str=str(cache_row.id),
                query_text=cache_row.query_text,
                response_text=cache_row.response_text,
                embedding=q_vec,
                detected_mood=detected_mood,
                category=category,
                threshold=self.threshold,
                expires_at=expires_at,
                hit_count=0,
            )
            self._add_to_l1(mem_entry)

            logger.info(
                f"[SemanticCache] Cached in L1 + L2 for: '{query_text[:40]}...' (Threshold: {self.threshold})"
            )
            return True

        except Exception as exc:
            logger.error(f"[SemanticCache] Failed to store cache entry: {exc}")
            return False


cache_service = SemanticCacheService()
