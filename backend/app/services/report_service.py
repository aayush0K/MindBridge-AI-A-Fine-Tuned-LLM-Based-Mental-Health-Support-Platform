"""
Report Service
==============
Generates AI-powered mental wellness consultation summaries.
Aggregates the last N days of chat history + mood data, formats it into
a structured prompt, sends it to the inference service, and returns a
structured report suitable for download as a consultation summary.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from collections import Counter

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.message import Message
from app.models.session import ChatSession
from app.models.mood_log import MoodLog
from app.models.report import WellnessReport

logger = logging.getLogger(__name__)

INFERENCE_URL = "http://localhost:8001/generate"


async def generate_wellness_report(
    db: AsyncSession,
    user_id,
    days: int = 30,
) -> WellnessReport:
    """
    Generate a 30-day mental wellness consultation summary.

    Steps:
    1. Fetch all chat messages and mood logs for the period.
    2. Build a structured summary of patterns, topics, and mood trajectory.
    3. Send to the LLM for a professional-style written report.
    4. Save the report to the database.

    Returns the saved WellnessReport object.
    """
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)

    # ── Fetch chat history ────────────────────────────────────────────────────
    sessions_result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.started_at >= period_start,
        )
        .order_by(ChatSession.started_at)
    )
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]

    messages = []
    if session_ids:
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id.in_(session_ids))
            .order_by(Message.created_at)
            .limit(500)  # Cap to prevent context overflow
        )
        messages = msg_result.scalars().all()

    # ── Fetch mood logs ───────────────────────────────────────────────────────
    mood_result = await db.execute(
        select(MoodLog)
        .where(
            MoodLog.user_id == user_id,
            MoodLog.logged_at >= period_start,
        )
        .order_by(MoodLog.logged_at)
    )
    mood_logs = mood_result.scalars().all()

    # ── Build analysis data ───────────────────────────────────────────────────
    user_messages = [m for m in messages if m.role == "user"]
    mood_labels = [m.mood_label for m in mood_logs if m.mood_label]
    mood_scores = [m.mood_score for m in mood_logs]

    mood_frequency = dict(Counter(mood_labels).most_common(5))
    avg_mood = round(sum(mood_scores) / len(mood_scores), 1) if mood_scores else 0

    # Trend analysis
    if len(mood_scores) >= 4:
        mid = len(mood_scores) // 2
        first_half = sum(mood_scores[:mid]) / mid
        second_half = sum(mood_scores[mid:]) / (len(mood_scores) - mid)
        if second_half - first_half > 0.5:
            trend = "improving"
        elif first_half - second_half > 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient data"

    # Extract key conversation snippets (first 20 user messages)
    conversation_sample = "\n".join(
        [f"- \"{m.content[:150]}\"" for m in user_messages[:20]]
    )

    # ── Build prompt for LLM ──────────────────────────────────────────────────
    report_prompt = f"""You are a mental health consultation report generator. Based on the following data from a user's {days}-day interaction history with a mental health support platform, generate a professional, empathetic wellness summary report.

DATA:
- Total conversations: {len(sessions)}
- Total messages exchanged: {len(messages)}
- Average mood score: {avg_mood}/10
- Mood trend: {trend}
- Most frequent emotions: {json.dumps(mood_frequency)}
- Sample user concerns:
{conversation_sample}

INSTRUCTIONS:
1. Write a professional summary paragraph (3-5 sentences) describing the user's overall emotional state and patterns observed.
2. List 3-5 key topics or themes the user discussed.
3. Provide 3-5 specific, actionable wellness recommendations.
4. Note any areas where professional help might be beneficial.
5. Keep the tone warm, supportive, and professional — suitable for sharing with a counselor.
6. Do NOT diagnose any conditions. Focus on observed patterns and supportive guidance.

FORMAT your response as JSON:
{{
    "summary": "...",
    "key_topics": ["topic1", "topic2", ...],
    "recommendations": "...",
    "professional_referral_note": "..."
}}"""

    # ── Call inference service ─────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a professional mental health report generator. Output valid JSON only."},
                    {"role": "user", "content": report_prompt}
                ],
                "temperature": 0.3,
                "max_new_tokens": 800,
            }
            response = await client.post(INFERENCE_URL, json=payload)
            response.raise_for_status()
            llm_output = response.json().get("response", "")
    except Exception as e:
        logger.error(f"[ReportService] LLM call failed: {e}")
        # Generate a rule-based fallback report
        llm_output = None

    # ── Parse LLM output or use fallback ──────────────────────────────────────
    key_topics_list = list(mood_frequency.keys())
    if llm_output:
        try:
            # Try to extract JSON from the response
            json_start = llm_output.find("{")
            json_end = llm_output.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(llm_output[json_start:json_end])
                summary_text = parsed.get("summary", "")
                key_topics_list = parsed.get("key_topics", key_topics_list)
                recommendations_text = parsed.get("recommendations", "")
                if parsed.get("professional_referral_note"):
                    recommendations_text += f"\n\nNote: {parsed['professional_referral_note']}"
            else:
                summary_text = llm_output
                recommendations_text = ""
        except (json.JSONDecodeError, ValueError):
            summary_text = llm_output
            recommendations_text = ""
    else:
        # Rule-based fallback
        summary_text = (
            f"Over the past {days} days, this user engaged in {len(sessions)} conversations "
            f"with {len(messages)} total messages exchanged. Their average mood score was "
            f"{avg_mood}/10 with a {trend} trajectory. "
            f"The most frequently expressed emotions were: {', '.join(mood_frequency.keys()) or 'not enough data'}."
        )
        recommendations_text = (
            "1. Continue regular check-ins with the platform.\n"
            "2. Practice mindfulness techniques when feeling overwhelmed.\n"
            "3. Consider speaking with a licensed counselor for deeper support."
        )

    # ── Save report ───────────────────────────────────────────────────────────
    report = WellnessReport(
        user_id=user_id,
        period_start=period_start,
        period_end=now,
        summary=summary_text,
        key_topics=key_topics_list,
        mood_analysis={
            "average_score": avg_mood,
            "trend": trend,
            "emotion_frequency": mood_frequency,
            "total_mood_entries": len(mood_logs),
        },
        recommendations=recommendations_text,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    return report
