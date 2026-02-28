"""
Mock Data API Endpoints for KlyrSignals

Provides endpoints for loading demo data for screenshots and testing.
"""

from fastapi import APIRouter
from app.data.mock_portfolio import MOCK_PORTFOLIO, MOCK_ANALYSIS

router = APIRouter()


@router.get("/portfolio")
async def get_mock_portfolio():
    """Return mock portfolio data for demo/screenshots"""
    return MOCK_PORTFOLIO


@router.get("/analysis")
async def get_mock_analysis():
    """Return mock analysis results for demo/screenshots"""
    return MOCK_ANALYSIS


@router.post("/load")
async def load_mock_data():
    """Load mock data into localStorage (returns data for frontend to store)"""
    from datetime import datetime
    
    return {
        "portfolio": {
            "holdings": MOCK_PORTFOLIO["holdings"],
            "total_value": MOCK_PORTFOLIO["total_value"],
            "cash": MOCK_PORTFOLIO["cash"],
            "last_updated": datetime.utcnow().isoformat() + "Z"
        },
        "analysis": MOCK_ANALYSIS,
        "message": "Mock data loaded successfully"
    }
