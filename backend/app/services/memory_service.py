"""
MemoryService — Redis-backed Conversation Memory
=================================================
Stores the last N messages per chat session as a Redis **List** (newest last).
All writes are atomic RPUSH+LTRIM pipelines — no read-modify-write race.
TTL is refreshed on every write so idle sessions are auto-expired.

Design decisions
----------------
* Key schema : "mb:memory:{session_id}"  (easy to namespace / flush)
* Storage    : Redis List; each element is a JSON-encoded message dict.
               RPUSH to append, LTRIM to cap, LRANGE to read — all O(1)/O(N).
* Atomicity  : RPUSH + LTRIM + EXPIRE run in a single pipeline (no race).
* TTL        : Reset on every write — 24 hours by default.
* Graceful   : If Redis is unavailable the service returns empty history and
               the chat pipeline continues without memory until Redis recovers.
               The _available flag is updated on every operation failure.

Message dict schema stored in Redis
--------------------------------------
{
    "role"       : "user" | "assistant",
    "content"    : str,
    "category"   : str | None,          # classifier output for user turns
    "confidence" : float | None,        # classifier confidence
    "is_crisis"  : bool,                # crisis flag from this turn
    "timestamp"  : float                # Unix epoch (for debugging / audit)
}
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
REDIS_KEY_PREFIX = "mb:memory:"
MAX_HISTORY      = 20       # max messages kept per session (10 turns)
HISTORY_FOR_LLM  = 12       # how many recent messages to inject (6 turns)
TTL_SECONDS      = 86_400   # 24 hours — reset on every write


class MemoryService:
    """
    Async Redis-backed conversation memory using atomic list operations.

    Lifecycle
    ---------
    1. Call ``await initialize()`` once at FastAPI startup.
    2. Use ``get_history()`` / ``append_message()`` per request.
    3. Call ``close()`` at shutdown.
    """

    def __init__(self) -> None:
        self._client: Optional[aioredis.Redis] = None
        self._available: bool = False

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Create Redis client and verify connectivity."""
        try:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            await self._client.ping()
            self._available = True
            logger.info(
                f"[MemoryService] Connected to Redis at {settings.REDIS_URL}"
            )
        except Exception as exc:
            self._available = False
            logger.warning(
                f"[MemoryService] Redis unavailable ({exc}). "
                "Chat memory disabled — system continues without it."
            )

    async def close(self) -> None:
        """Gracefully close the Redis connection."""
        if self._client:
            await self._client.aclose()
            logger.info("[MemoryService] Redis connection closed.")

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _build_key(session_id: str) -> str:
        return f"{REDIS_KEY_PREFIX}{session_id}"

    def _mark_unavailable(self, exc: Exception, context: str) -> None:
        """Log the failure and mark service as unavailable for future checks."""
        logger.warning(f"[MemoryService] {context}: {exc}")
        self._available = False

    # ── Public API ───────────────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        """True when the Redis connection is currently considered live."""
        return self._available

    async def get_history(
        self,
        session_id: str,
        limit: int = HISTORY_FOR_LLM,
    ) -> list[dict]:
        """
        Return the last `limit` messages for this session.
        Uses LRANGE to read the tail of the list — O(limit), not O(N).
        Returns [] when Redis is unavailable or the session has no history.
        """
        if not self._available or not self._client:
            return []
        key = self._build_key(session_id)
        try:
            # LRANGE -limit -1 gives the last `limit` elements
            raw_items = await self._client.lrange(key, -limit, -1)
            return [json.loads(item) for item in raw_items]
        except Exception as exc:
            self._mark_unavailable(exc, f"Read error for {key}")
            return []

    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        category: Optional[str] = None,
        confidence: Optional[float] = None,
        is_crisis: bool = False,
    ) -> None:
        """
        Atomically append one message and enforce the rolling window.

        Uses a Redis pipeline:
          RPUSH  key  json_payload   → append to tail
          LTRIM  key  -MAX_HISTORY 0 → cap list length (keeps newest)
          EXPIRE key  TTL_SECONDS    → reset TTL

        All three commands execute in a single round-trip with no race.

        Parameters
        ----------
        session_id  : UUID string (from chat session)
        role        : "user" or "assistant"
        content     : The message text
        category    : Classifier-predicted category (user turns only)
        confidence  : Classifier confidence (user turns only)
        is_crisis   : Whether this turn triggered crisis protocol
        """
        if not self._available or not self._client:
            return

        key = self._build_key(session_id)
        entry = json.dumps(
            {
                "role"      : role,
                "content"   : content,
                "category"  : category,
                "confidence": confidence,
                "is_crisis" : is_crisis,
                "timestamp" : time.time(),
            },
            ensure_ascii=False,
        )

        try:
            async with self._client.pipeline(transaction=True) as pipe:
                pipe.rpush(key, entry)
                pipe.ltrim(key, -MAX_HISTORY, -1)
                pipe.expire(key, TTL_SECONDS)
                await pipe.execute()
        except Exception as exc:
            self._mark_unavailable(exc, f"Write error for {key}")

    async def append_turn(
        self,
        session_id: str,
        *,
        user_message: str,
        ai_message: str,
        category: str | None = None,
        confidence: float | None = None,
    ) -> None:
        """
        Atomically write a full user+assistant turn in ONE Redis round-trip.

        Uses a single pipeline:
          RPUSH key user_entry  → append user message
          RPUSH key ai_entry    → append assistant message
          LTRIM key -MAX_HISTORY -1  → enforce rolling window
          EXPIRE key TTL_SECONDS     → reset TTL

        This halves the Redis network overhead vs. two separate append_message calls.
        """
        if not self._available or not self._client:
            return

        key = self._build_key(session_id)
        now = time.time()

        user_entry = json.dumps(
            {"role": "user", "content": user_message, "category": category,
             "confidence": confidence, "is_crisis": False, "timestamp": now},
            ensure_ascii=False,
        )
        ai_entry = json.dumps(
            {"role": "assistant", "content": ai_message, "category": None,
             "confidence": None, "is_crisis": False, "timestamp": now + 0.001},
            ensure_ascii=False,
        )

        try:
            async with self._client.pipeline(transaction=True) as pipe:
                pipe.rpush(key, user_entry)
                pipe.rpush(key, ai_entry)
                pipe.ltrim(key, -MAX_HISTORY, -1)
                pipe.expire(key, TTL_SECONDS)
                await pipe.execute()
        except Exception as exc:
            self._mark_unavailable(exc, f"Append turn error for {key}")

    async def clear_session(self, session_id: str) -> None:
        """Delete all memory for a session (e.g. user deletes conversation)."""
        if not self._available or not self._client:
            return
        try:
            await self._client.delete(self._build_key(session_id))
        except Exception as exc:
            self._mark_unavailable(exc, f"Delete error for {session_id}")

    async def ping(self) -> bool:
        """Health-check helper — used by /health endpoint."""
        if not self._client:
            return False
        try:
            result = await self._client.ping()
            if result:
                self._available = True  # restore if Redis recovered
            return bool(result)
        except Exception:
            self._available = False
            return False


# ── Singleton — initialised once at FastAPI startup (same pattern as embedder) ──
memory_service = MemoryService()
