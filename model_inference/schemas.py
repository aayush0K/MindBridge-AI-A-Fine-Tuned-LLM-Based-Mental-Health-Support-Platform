from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class InferenceRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = None
    message: Optional[str] = None
    prompt: Optional[str] = None
    temperature: float = Field(default=0.6, ge=0.0, le=2.0)
    max_new_tokens: int = Field(default=300, ge=1, le=2048)

class InferenceResponse(BaseModel):
    response: str
    model: str
    generation_time_ms: float
