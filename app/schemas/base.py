"""Base schema and shared types."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with strict configuration."""

    model_config = ConfigDict(strict=True, from_attributes=True)


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    id: uuid.UUID
