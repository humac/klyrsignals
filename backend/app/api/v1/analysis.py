"""
Analysis endpoints - Risk score, blind spots, recommendations
"""

from fastapi import APIRouter, HTTPException, Query
import json
from app.models.holding import Holding
from app.models.portfolio import (
    RiskScoreResponse,
    RecommendationResponse,
    BlindSpotResponse,
    PortfolioAnalysisRequest,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["analysis"])


@router.get("/api/v1/risk-score", response_model=RiskScoreResponse)
async def get_risk_score(holdings: str = Query(..., description="JSON-encoded list of holdings")):
    """
    Calculate portfolio risk score (0-100).
    
    - **holdings**: JSON-encoded list of holdings
    - **Returns**: Risk score with breakdown
    """
    try:
        holdings_list = [Holding(**h) for h in json.loads(holdings)]
        
        portfolio_service = PortfolioService()
        # We need to fetch prices first
        from app.services.market_data_service import get_market_data_service
        market_data = get_market_data_service()
        symbols = [h.symbol for h in holdings_list]
        prices = await market_data.get_prices(symbols)
        
        # Use purchase price as fallback
        for holding in holdings_list:
            if prices.get(holding.symbol) is None:
                prices[holding.symbol] = holding.purchase_price
        
        from app.core.scoring import calculate_risk_score
        risk_score, risk_breakdown = calculate_risk_score(holdings_list, prices)
        
        return RiskScoreResponse(
            risk_score=risk_score,
            risk_breakdown=risk_breakdown,
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in holdings parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")


@router.post("/api/v1/blind-spots", response_model=BlindSpotResponse)
async def detect_blind_spots(request: PortfolioAnalysisRequest):
    """
    Detect hidden concentration risks and blind spots.
    
    - **holdings**: List of portfolio holdings
    - **Returns**: List of detected blind spots with confidence scores
    """
    try:
        portfolio_service = PortfolioService()
        # Use the internal method
        from app.services.market_data_service import get_market_data_service
        market_data = get_market_data_service()
        symbols = [h.symbol for h in request.holdings]
        prices = await market_data.get_prices(symbols)
        
        # Calculate sector allocation
        from app.core.allocation import calculate_allocation
        _, sector_allocation = calculate_allocation(request.holdings, prices)
        
        blind_spots = portfolio_service._detect_blind_spots(request.holdings, sector_allocation)
        
        return BlindSpotResponse(blind_spots=blind_spots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blind spot detection failed: {str(e)}")


@router.get("/api/v1/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    holdings: str = Query(..., description="JSON-encoded list of holdings"),
    target_allocation: str = Query(None, description="Optional target allocation JSON")
):
    """
    Generate rebalancing recommendations.
    
    - **holdings**: JSON-encoded list of holdings
    - **target_allocation**: Optional target allocation JSON
    - **Returns**: Prioritized list of rebalancing actions
    """
    try:
        holdings_list = [Holding(**h) for h in json.loads(holdings)]
        
        portfolio_service = PortfolioService()
        from app.services.market_data_service import get_market_data_service
        market_data = get_market_data_service()
        symbols = [h.symbol for h in holdings_list]
        prices = await market_data.get_prices(symbols)
        
        # Use purchase price as fallback
        for holding in holdings_list:
            if prices.get(holding.symbol) is None:
                prices[holding.symbol] = holding.purchase_price
        
        # Calculate allocations
        from app.core.allocation import calculate_allocation
        asset_class_allocation, sector_allocation = calculate_allocation(holdings_list, prices)
        
        recommendations = portfolio_service._generate_recommendations(
            holdings_list, prices, sector_allocation, asset_class_allocation
        )
        
        return RecommendationResponse(recommendations=recommendations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in holdings parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")
