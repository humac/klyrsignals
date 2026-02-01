"""User schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr

from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr


class UserResponse(BaseSchema):
    id: uuid.UUID
    email: str
    snaptrade_user_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "strict": False}
