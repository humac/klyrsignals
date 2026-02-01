"""Position and holdings schemas."""

import uuid
from datetime import datetime

from app.schemas.base import BaseSchema


class PositionResponse(BaseSchema):
    id: uuid.UUID
    account_id: uuid.UUID
    symbol: str
    description: str | None = None
    asset_class: str
    units: float
    cost_basis_cents: int
    market_value_cents: int
    currency: str
    exchange: str | None = None
    last_price_cents: int
    updated_at: datetime

    model_config = {"from_attributes": True, "strict": False}


class AccountSummary(BaseSchema):
    account_id: uuid.UUID
    account_name: str
    account_type: str | None = None
    currency: str
    total_market_value_cents: int
    total_cost_basis_cents: int
    gain_loss_cents: int
    gain_loss_pct: float
    positions: list[PositionResponse]

    model_config = {"strict": False}


class PortfolioSummary(BaseSchema):
    user_id: uuid.UUID
    total_market_value_cents: int
    total_cost_basis_cents: int
    total_gain_loss_cents: int
    total_gain_loss_pct: float
    accounts: list[AccountSummary]

    model_config = {"strict": False}
