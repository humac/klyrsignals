"""
Portfolio models - request/response schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.holding import Holding
from app.models.common import Warning, Recommendation, BlindSpot


class PortfolioAnalysisRequest(BaseModel):
    """
    Request model for portfolio analysis.
    """
    holdings: list[Holding] = Field(
        ...,
        min_length=1,
        description="List of portfolio holdings to analyze"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "holdings": [
                    {
                        "symbol": "AAPL",
                        "quantity": 50,
                        "purchase_price": 150.00,
                        "purchase_date": "2024-01-15",
                        "asset_class": "stock"
                    },
                    {
                        "symbol": "MSFT",
                        "quantity": 30,
                        "purchase_price": 280.00,
                        "purchase_date": "2024-02-20",
                        "asset_class": "stock"
                    }
                ]
            }
        }


class RiskBreakdown(BaseModel):
    """
    Breakdown of risk score by category.
    """
    concentration: int = Field(..., ge=0, le=50, description="Concentration risk (0-50)")
    volatility: int = Field(..., ge=0, le=30, description="Volatility risk (0-30)")
    correlation: int = Field(..., ge=0, le=20, description="Correlation risk (0-20)")


class PortfolioAnalysis(BaseModel):
    """
    Complete portfolio analysis response.
    """
    total_value: float = Field(..., ge=0, description="Total portfolio value in USD")
    total_cost_basis: float = Field(..., ge=0, description="Total cost basis in USD")
    total_gain_loss: float = Field(..., description="Total gain/loss in USD")
    total_gain_loss_pct: float = Field(..., description="Total gain/loss percentage")
    allocation: dict[str, float] = Field(..., description="Allocation by asset class (percentages)")
    sector_allocation: dict[str, float] = Field(..., description="Allocation by sector (percentages)")
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100, lower is better)")
    risk_breakdown: RiskBreakdown
    warnings: list[Warning] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    blind_spots: list[BlindSpot] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_value": 29800.00,
                "total_cost_basis": 22900.00,
                "total_gain_loss": 6900.00,
                "total_gain_loss_pct": 30.13,
                "allocation": {"stock": 67.8, "etf": 32.2},
                "sector_allocation": {"Technology": 55.4, "Broad Market": 32.2, "Cash": 12.4},
                "risk_score": 58,
                "risk_breakdown": {
                    "concentration": 30,
                    "volatility": 18,
                    "correlation": 10
                },
                "warnings": [
                    {
                        "type": "sector_concentration",
                        "severity": "medium",
                        "message": "Technology sector represents 55.4% of portfolio",
                        "details": {"sector": "Technology", "percentage": 55.4},
                        "affected_symbols": ["AAPL", "MSFT"]
                    }
                ],
                "recommendations": [
                    {
                        "action": "sell",
                        "symbol": "AAPL",
                        "quantity": 15,
                        "reason": "Reduce Technology exposure from 55% to 40%",
                        "priority": 2,
                        "expected_impact": "Reduce risk score by 8 points"
                    }
                ],
                "blind_spots": [
                    {
                        "type": "style_concentration",
                        "confidence": 78,
                        "message": "Portfolio heavily tilted toward large-cap growth stocks",
                        "details": {"dominant_style": "large_cap_growth", "percentage": 82},
                        "affected_symbols": ["AAPL", "MSFT"]
                    }
                ],
                "timestamp": "2026-02-28T19:00:00Z"
            }
        }


class RiskScoreResponse(BaseModel):
    """
    Risk score response model.
    """
    risk_score: int = Field(..., ge=0, le=100)
    risk_breakdown: RiskBreakdown
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecommendationResponse(BaseModel):
    """
    Recommendations response model.
    """
    recommendations: list[Recommendation]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BlindSpotResponse(BaseModel):
    """
    Blind spots response model.
    """
    blind_spots: list[BlindSpot]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PriceResponse(BaseModel):
    """
    Price response model.
    """
    prices: dict[str, float | None]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "yfinance"
