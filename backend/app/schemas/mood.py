from pydantic import BaseModel
from datetime import datetime
import uuid


class MoodLogRequest(BaseModel):
    mood_score: int
    mood_label: str | None = None
    notes: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "mood_score": 7,
                "mood_label": "calm",
                "notes": "Had a good workout today"
            }
        }


class MoodLogResponse(BaseModel):
    id: uuid.UUID
    mood_score: int
    mood_label: str | None
    notes: str | None
    logged_at: datetime
    auto_detected: bool = False
    confidence: float | None = None
    raw_label: str | None = None

    class Config:
        from_attributes = True


class MoodStatsResponse(BaseModel):
    avg_score: float
    most_common_label: str | None
    trend: str  # "improving", "declining", "stable"
    total_logs: int


class MoodTrendPoint(BaseModel):
    date: str  # ISO date string
    avg_score: float
    dominant_mood: str | None


class MoodTrendResponse(BaseModel):
    daily_trend: list[MoodTrendPoint]
    weekly_avg: float
    monthly_avg: float
    most_frequent_emotions: list[dict]  # [{"label": "Anxious", "count": 12}, ...]
    total_auto_detected: int
    trend_direction: str  # "improving", "declining", "stable"
