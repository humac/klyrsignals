"""
Portfolio analysis endpoints
"""

from fastapi import APIRouter, HTTPException
from app.models.portfolio import PortfolioAnalysisRequest, PortfolioAnalysis
from app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["portfolio"])


@router.post("/api/v1/analyze", response_model=PortfolioAnalysis)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Analyze portfolio holdings and return comprehensive analysis.
    
    - **holdings**: List of portfolio holdings
    - **Returns**: Complete analysis including allocation, risk score, warnings, recommendations
    """
    try:
        portfolio_service = PortfolioService()
        analysis = await portfolio_service.analyze(request.holdings)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
