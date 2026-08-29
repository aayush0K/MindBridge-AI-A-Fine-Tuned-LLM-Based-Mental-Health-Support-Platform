"""
WebSocket endpoint for real-time streaming chat.
ws://localhost:8000/ws/chat/{session_id}?token=<jwt>

Key design decisions
---------------------
* Auth + session-resolve uses a short-lived DB transaction that closes
  BEFORE the while-True loop. Holding a connection for a long-lived WS
  connection would exhaust pool_size=5 with just 5 concurrent users.
* Each incoming message acquires its own fresh DB session (msg_db) for
  the write path, then releases it immediately after flush.
* `session_id_obj` carries the resolved UUID out of the auth block.
"""

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select, update
import json
import logging

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.session import ChatSession
from app.models.message import Message
from app.services.auth_service import decode_token
from app.services.ai_service import process_message
from jose import JWTError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
):
    await websocket.accept()

    # ── Token validation ──────────────────────────────────────────────────────
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            await websocket.send_json({"error": "Invalid token type"})
            await websocket.close(code=4001)
            return
        user_id = payload.get("sub")
    except JWTError:
        await websocket.send_json({"error": "Invalid or expired token"})
        await websocket.close(code=4001)
        return

    # ── Auth + session resolution — short-lived DB transaction ───────────────
    # This block MUST exit before the while-True loop so the DB connection
    # is returned to the pool. With pool_size=5, just 5 long-lived WS
    # connections would otherwise starve the REST API entirely.
    user_email: str = ""
    session_id_obj: uuid.UUID | None = None

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            await websocket.send_json({"error": "User not found"})
            await websocket.close(code=4003)
            return

        user_email = user.email

        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            await websocket.send_json({"error": "Invalid session_id"})
            await websocket.close(code=4000)
            return

        session_result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == sid,
                ChatSession.user_id == user.id,
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            session = ChatSession(id=sid, user_id=user.id)
            db.add(session)
            await db.flush()

        session_id_obj = session.id
        # ← DB session context exits here; connection returned to pool

    await websocket.send_json({"type": "connected", "session_id": str(session_id_obj)})

    # ── Message loop ──────────────────────────────────────────────────────────
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                user_message = data.get("message", "").strip()
            except json.JSONDecodeError:
                user_message = raw.strip()

            if not user_message:
                continue

            await websocket.send_json({"type": "typing"})

            # Fresh DB session per message — acquired and released immediately
            async with AsyncSessionLocal() as msg_db:
                # Fallback history (used only when Redis is unavailable)
                history_result = await msg_db.execute(
                    select(Message)
                    .where(Message.session_id == session_id_obj)
                    .order_by(Message.created_at)
                    .limit(20)
                )
                history = [
                    {"role": m.role, "content": m.content}
                    for m in history_result.scalars().all()
                ]

                ai_result = await process_message(
                    user_message=user_message,
                    session_id=str(session_id_obj),
                    session_history=history,
                )

                msg_db.add(Message(
                    session_id=session_id_obj,
                    role="user",
                    content=user_message,
                    relevance_score=ai_result["relevance_score"],
                    is_crisis=ai_result.get("is_crisis", False),
                ))
                msg_db.add(Message(
                    session_id=session_id_obj,
                    role="assistant",
                    content=ai_result["response"],
                    relevance_score=ai_result["relevance_score"],
                    is_crisis=ai_result["is_crisis"],
                ))

                # Use SQL increment to avoid the in-Python counter race
                await msg_db.execute(
                    update(ChatSession)
                    .where(ChatSession.id == session_id_obj)
                    .values(
                        message_count=ChatSession.message_count + 2,
                        crisis_flagged=ai_result["is_crisis"] or ChatSession.crisis_flagged,
                    )
                )
                await msg_db.flush()

            await websocket.send_json({
                "type": "message",
                "response": ai_result["response"],
                "is_crisis": ai_result["is_crisis"],
                "is_relevant": ai_result["is_relevant"],
                "relevance_score": ai_result["relevance_score"],
                "few_shot_count": ai_result["few_shot_count"],
                "predicted_category": ai_result.get("predicted_category"),
                "classifier_confidence": ai_result.get("classifier_confidence", 0.0),
                "memory_used": ai_result.get("memory_used", False),
            })

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected: {user_email} / session {session_id_obj}")
    except Exception as e:
        logger.error(f"[WS] Error for session {session_id_obj}: {e}")
        try:
            await websocket.send_json({"type": "error", "message": "An error occurred"})
        except Exception:
            pass
