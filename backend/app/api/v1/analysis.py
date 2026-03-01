from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user, TokenData
from app.services.database import db
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import PortfolioAnalysis

router = APIRouter()

@router.get("/", response_model=PortfolioAnalysis)
async def analyze_portfolio(current_user: TokenData = Depends(get_current_user)):
    """Analyze current user's portfolio"""
    # Get portfolio with holdings
    portfolio = await db.portfolio.find_first(
        where={"userId": current_user.user_id},
        include={"holdings": True}
    )
    
    if not portfolio or not portfolio.holdings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No holdings to analyze. Please import or add holdings first."
        )
    
    # Convert to format expected by PortfolioService
    holdings = [
        {
            "symbol": h.symbol,
            "quantity": h.quantity,
            "purchase_price": h.purchasePrice,
        }
        for h in portfolio.holdings
    ]
    
    # Perform analysis
    portfolio_service = PortfolioService()
    analysis = await portfolio_service.analyze(holdings)
    
    return analysis
