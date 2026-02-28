"""
Common models - Warning, Recommendation, BlindSpot
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class WarningSeverity(str, Enum):
    """Warning severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WarningType(str, Enum):
    """Types of warnings"""
    SECTOR_CONCENTRATION = "sector_concentration"
    SINGLE_STOCK = "single_stock"
    ASSET_CLASS_IMBALANCE = "asset_class_imbalance"
    GEOGRAPHIC_CONCENTRATION = "geographic_concentration"


class Warning(BaseModel):
    """
    Represents a risk warning detected in a portfolio.
    """
    type: WarningType
    severity: WarningSeverity
    message: str
    details: dict = Field(default_factory=dict)
    affected_symbols: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "sector_concentration",
                "severity": "critical",
                "message": "Portfolio is 100% exposed to Technology sector",
                "details": {"sector": "Technology", "percentage": 100.0},
                "affected_symbols": ["AAPL", "MSFT", "GOOGL"]
            }
        }


class RecommendationAction(str, Enum):
    """Recommendation action types"""
    SELL = "sell"
    BUY = "buy"
    HOLD = "hold"


class Recommendation(BaseModel):
    """
    Represents a rebalancing recommendation.
    """
    action: RecommendationAction
    symbol: str
    quantity: Optional[float] = Field(None, gt=0)
    reason: str
    priority: int = Field(..., ge=1, le=10, description="Priority (1=highest, 10=lowest)")
    expected_impact: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "sell",
                "symbol": "AAPL",
                "quantity": 20,
                "reason": "Reduce single-stock concentration from 25% to 15%",
                "priority": 1,
                "expected_impact": "Reduce risk score by 12 points"
            }
        }


class BlindSpotType(str, Enum):
    """Types of blind spots"""
    HIDDEN_CORRELATION = "hidden_correlation"
    STYLE_CONCENTRATION = "style_concentration"
    GEOGRAPHIC_CONCENTRATION = "geographic_concentration"
    MARKET_CAP_CONCENTRATION = "market_cap_concentration"


class BlindSpot(BaseModel):
    """
    Represents a blind spot detected by AI analysis.
    """
    type: BlindSpotType
    confidence: int = Field(..., ge=0, le=100, description="Confidence score (0-100%)")
    message: str
    details: dict = Field(default_factory=dict)
    affected_symbols: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "style_concentration",
                "confidence": 78,
                "message": "Portfolio heavily tilted toward large-cap growth stocks",
                "details": {
                    "dominant_style": "large_cap_growth",
                    "percentage": 82
                },
                "affected_symbols": ["AAPL", "MSFT"]
            }
        }
