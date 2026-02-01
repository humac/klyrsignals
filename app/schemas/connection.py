"""Connection schemas."""

import uuid
from datetime import datetime

from app.schemas.base import BaseSchema


class ConnectionCreate(BaseSchema):
    """Start a SnapTrade connection flow."""
    user_id: uuid.UUID
    brokerage_name: str = "Wealthsimple"


class ConnectionResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    brokerage_name: str
    status: str
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "strict": False}


class SnapTradeRedirectResponse(BaseSchema):
    """Response with SnapTrade connection portal URL."""
    redirect_url: str
    connection_id: uuid.UUID

    model_config = {"strict": False}
