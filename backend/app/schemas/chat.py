from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict
from datetime import datetime
import uuid


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message text")
    session_id: uuid.UUID | None = None

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    relevance_score: float | None
    is_crisis: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    # Core response
    response: str
    session_id: uuid.UUID

    # Safety signals
    is_crisis: bool

    # Relevance / retrieval metadata
    is_relevant: bool
    relevance_score: float
    few_shot_count: int

    # Classifier enrichment (None when model not yet trained)
    predicted_category: str | None = None
    classifier_confidence: float = 0.0
    uncertainty: float = 0.0

    # Memory
    memory_used: bool = False

    # Phase 7: Automated mood detection
    detected_mood: str | None = None
    mood_confidence: float = 0.0


class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    message_count: int
    crisis_flagged: bool
    started_at: datetime

    model_config = ConfigDict(from_attributes=True)
