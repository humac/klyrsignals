"""Analysis schemas for blind spot detection results."""

import uuid
from datetime import datetime

from app.schemas.base import BaseSchema


class ConcentrationAlert(BaseSchema):
    """A single concentration warning."""
    category: str  # sector, country, asset_class
    name: str  # e.g., "Financials", "Canada"
    weight_pct: float
    threshold_pct: float
    severity: str  # warning, critical

    model_config = {"strict": False}


class HiddenTwin(BaseSchema):
    """A pair of highly correlated holdings."""
    symbol_a: str
    symbol_b: str
    correlation: float
    explanation: str

    model_config = {"strict": False}


class ConcentrationReport(BaseSchema):
    alerts: list[ConcentrationAlert]
    sector_weights: dict[str, float]
    country_weights: dict[str, float]
    home_bias_pct: float

    model_config = {"strict": False}


class CorrelationReport(BaseSchema):
    hidden_twins: list[HiddenTwin]
    correlation_matrix: dict[str, dict[str, float]]

    model_config = {"strict": False}


class KlyrSignal(BaseSchema):
    """A single AI-generated strategic signal."""
    signal_id: str
    title: str
    description: str
    severity: str  # info, warning, critical
    category: str  # concentration, correlation, home_bias, interest_rate
    affected_holdings: list[str]
    recommendation: str

    model_config = {"strict": False}


class FullAnalysisResponse(BaseSchema):
    user_id: uuid.UUID
    concentration: ConcentrationReport
    correlation: CorrelationReport
    signals: list[KlyrSignal]
    ai_summary: str
    analyzed_at: datetime

    model_config = {"strict": False}
