from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from collections import Counter

from app.database import get_db
from app.models.mood_log import MoodLog
from app.models.user import User
from app.schemas.mood import (
    MoodLogRequest, MoodLogResponse, MoodStatsResponse,
    MoodTrendResponse, MoodTrendPoint,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/mood", tags=["Mood"])


@router.post("/log", response_model=MoodLogResponse, status_code=201)
async def log_mood(
    data: MoodLogRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not 1 <= data.mood_score <= 10:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="mood_score must be between 1 and 10")

    log = MoodLog(
        user_id=current_user.id,
        mood_score=data.mood_score,
        mood_label=data.mood_label,
        notes=data.notes,
        auto_detected=False,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.get("/history", response_model=list[MoodLogResponse])
async def get_mood_history(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id, MoodLog.logged_at >= since)
        .order_by(MoodLog.logged_at.desc())
    )
    return result.scalars().all()


@router.get("/stats", response_model=MoodStatsResponse)
async def get_mood_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Last 30 days
    since = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id, MoodLog.logged_at >= since)
        .order_by(MoodLog.logged_at)
    )
    logs = result.scalars().all()

    if not logs:
        return MoodStatsResponse(avg_score=0, most_common_label=None, trend="stable", total_logs=0)

    scores = [l.mood_score for l in logs]
    avg = sum(scores) / len(scores)

    labels = [l.mood_label for l in logs if l.mood_label]
    most_common = Counter(labels).most_common(1)[0][0] if labels else None

    # Trend: compare first half avg vs second half avg
    if len(scores) >= 4:
        mid = len(scores) // 2
        first_avg = sum(scores[:mid]) / mid
        second_avg = sum(scores[mid:]) / (len(scores) - mid)
        if second_avg - first_avg > 0.5:
            trend = "improving"
        elif first_avg - second_avg > 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return MoodStatsResponse(
        avg_score=round(avg, 1),
        most_common_label=most_common,
        trend=trend,
        total_logs=len(logs),
    )


# ── Phase 8: Automated Mood Trend Endpoint ────────────────────────────────────

@router.get("/trends", response_model=MoodTrendResponse)
async def get_mood_trends(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns aggregated automated mood trends for the dashboard.
    Groups auto-detected moods by day, calculates weekly/monthly averages,
    identifies the most frequent emotions, and determines the overall trend direction.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(MoodLog)
        .where(
            MoodLog.user_id == current_user.id,
            MoodLog.logged_at >= since,
            MoodLog.auto_detected == True,
        )
        .order_by(MoodLog.logged_at)
    )
    logs = result.scalars().all()

    # ── Daily aggregation ──────────────────────────────────────────────────
    daily: dict[str, list] = {}
    for log in logs:
        day_key = log.logged_at.strftime("%Y-%m-%d")
        daily.setdefault(day_key, []).append(log)

    daily_trend = []
    for day_key, day_logs in sorted(daily.items()):
        scores = [l.mood_score for l in day_logs]
        labels = [l.mood_label for l in day_logs if l.mood_label]
        dominant = Counter(labels).most_common(1)[0][0] if labels else None
        daily_trend.append(MoodTrendPoint(
            date=day_key,
            avg_score=round(sum(scores) / len(scores), 1),
            dominant_mood=dominant,
        ))

    # ── Weekly / Monthly averages ──────────────────────────────────────────
    all_scores = [l.mood_score for l in logs]
    monthly_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_scores = [
        l.mood_score
        for l in logs
        if (
            l.logged_at.replace(tzinfo=timezone.utc)
            if l.logged_at.tzinfo is None
            else l.logged_at
        )
        >= week_ago
    ]
    weekly_avg = round(sum(weekly_scores) / len(weekly_scores), 1) if weekly_scores else 0.0

    # ── Most frequent emotions ─────────────────────────────────────────────
    all_labels = [l.mood_label for l in logs if l.mood_label]
    emotion_counts = Counter(all_labels).most_common(5)
    most_frequent = [{"label": label, "count": count} for label, count in emotion_counts]

    # ── Trend direction ────────────────────────────────────────────────────
    if len(all_scores) >= 4:
        mid = len(all_scores) // 2
        first_avg = sum(all_scores[:mid]) / mid
        second_avg = sum(all_scores[mid:]) / (len(all_scores) - mid)
        if second_avg - first_avg > 0.5:
            trend_dir = "improving"
        elif first_avg - second_avg > 0.5:
            trend_dir = "declining"
        else:
            trend_dir = "stable"
    else:
        trend_dir = "stable"

    return MoodTrendResponse(
        daily_trend=daily_trend,
        weekly_avg=weekly_avg,
        monthly_avg=monthly_avg,
        most_frequent_emotions=most_frequent,
        total_auto_detected=len(logs),
        trend_direction=trend_dir,
    )
