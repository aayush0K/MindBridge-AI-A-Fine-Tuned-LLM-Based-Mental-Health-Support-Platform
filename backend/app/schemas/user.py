from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    emergency_email: EmailStr | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    emergency_email: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
