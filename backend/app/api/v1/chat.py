"""
Chat API — REST endpoints for chat sessions and message exchange.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from app.database import get_db
from app.models.user import User
from app.models.session import ChatSession
from app.models.message import Message
from app.models.mood_log import MoodLog
from app.schemas.chat import SendMessageRequest, ChatResponse, SessionResponse, MessageResponse
from app.services.ai_service import process_message
from app.services.memory_service import memory_service
from app.services.mood_service import mood_detector
from app.services.semantic_memory import store_message_embedding, search_semantic_memory
from app.services.embedder import embedder
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    data: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message and receive an AI response.

    The session history is loaded from Redis (fast, with TTL) when available,
    and falls back to PostgreSQL when Redis is unavailable.  Both sources are
    always written after each turn so they stay in sync.
    """
    # ── Get or create the chat session ─────────────────────────────────────
    session = None
    if data.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == data.session_id,
                ChatSession.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()

    if not session:
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        await db.flush()
        await db.refresh(session)

    # ── Load DB session history (Redis-fallback path in ai_service) ─────────
    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at)
        .limit(20)
    )
    history = history_result.scalars().all()
    session_history = [{"role": m.role, "content": m.content} for m in history]

    # ── Phase 9: Retrieve semantic memory (long-term context) ────────────────
    try:
        query_embedding = embedder.embed(data.message)
        semantic_memories = await search_semantic_memory(
            db, current_user.id, query_embedding, limit=3
        )
    except Exception:
        query_embedding = None
        semantic_memories = []

    # Inject semantic memories into session_history for LLM context
    if semantic_memories:
        memory_context = []
        for mem in semantic_memories:
            memory_context.append({
                "role": "user",
                "content": f"[Past context — {mem.get('mood', 'unknown')} mood]: {mem['content']}"
            })
        session_history = memory_context + session_history

    # ── Run AI pipeline ─────────────────────────────────────────────────────
    ai_result = await process_message(
        user_message=data.message,
        session_id=str(session.id),
        session_history=session_history,
    )

    # ── Persist to PostgreSQL (source of truth / audit trail) ───────────────
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=data.message,
        relevance_score=ai_result["relevance_score"],
        is_crisis=False,
    )
    db.add(user_msg)
    await db.flush()
    await db.refresh(user_msg)

    ai_msg = Message(
        session_id=session.id,
        role="assistant",
        content=ai_result["response"],
        relevance_score=ai_result["relevance_score"],
        is_crisis=ai_result["is_crisis"],
    )
    db.add(ai_msg)

    # ── Phase 7: Automated Mood Detection & Logging ──────────────────────────
    mood_result = mood_detector.detect(data.message)
    mood_log = MoodLog(
        user_id=current_user.id,
        mood_score=mood_result["mood_score"],
        mood_label=mood_result["mood_label"],
        notes=None,
        auto_detected=True,
        confidence=mood_result["confidence"],
        message_id=user_msg.id,
        raw_label=mood_result["raw_label"],
    )
    db.add(mood_log)

    # ── Phase 9: Store embedding for long-term semantic memory ───────────────
    if query_embedding is not None:
        await store_message_embedding(
            db,
            message_id=user_msg.id,
            embedding=query_embedding,
            user_id=current_user.id,
            detected_mood=mood_result["mood_label"],
            mood_confidence=mood_result["confidence"],
        )

    # ── Update session metadata via SQL to avoid race condition ────────────────
    # In-Python session.message_count += 2 is unsafe under concurrent requests
    # for the same session (two reads get same value, one write is lost).
    is_first_message = (session.message_count == 0)
    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session.id)
        .values(
            message_count=ChatSession.message_count + 2,
            crisis_flagged=ai_result["is_crisis"] or ChatSession.crisis_flagged,
        )
    )
    if is_first_message:
        title = data.message[:50] + ("..." if len(data.message) > 50 else "")
        await db.execute(
            update(ChatSession)
            .where(ChatSession.id == session.id)
            .values(title=title)
        )

    await db.flush()

    return ChatResponse(
        response=ai_result["response"],
        session_id=session.id,
        is_crisis=ai_result["is_crisis"],
        is_relevant=ai_result["is_relevant"],
        relevance_score=ai_result["relevance_score"],
        few_shot_count=ai_result["few_shot_count"],
        # New enrichment fields
        predicted_category=ai_result.get("predicted_category"),
        classifier_confidence=ai_result.get("classifier_confidence", 0.0),
        uncertainty=ai_result.get("uncertainty", 0.0),
        memory_used=ai_result.get("memory_used", False),
        # Phase 7: Mood detection result
        detected_mood=mood_result["mood_label"],
        mood_confidence=mood_result["confidence"],
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_session_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    session_result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Clear Redis memory for this session too
    await memory_service.clear_session(str(session_id))

    await db.delete(session)
    return {"message": "Session deleted"}
