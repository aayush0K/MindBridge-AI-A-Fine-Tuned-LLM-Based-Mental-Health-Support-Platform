from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class JournalCreate(BaseModel):
    title: str = Field(default="Untitled Reflection", max_length=255)
    content: str = Field(..., min_length=1)
    mood_tag: Optional[str] = Field(None, max_length=50)

class JournalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    mood_tag: Optional[str] = Field(None, max_length=50)

class JournalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    mood_tag: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
