from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.services.auth import get_current_user, TokenData
from app.services.database import db

router = APIRouter()

class HoldingImport(BaseModel):
    symbol: str
    quantity: float
    purchase_price: float
    asset_class: Optional[str] = "stock"

@router.get("/")
async def get_portfolio(current_user: TokenData = Depends(get_current_user)):
    """Get current user's portfolio"""
    portfolio = await db.portfolio_find_by_user(current_user.user_id)
    
    if not portfolio:
        # Create empty portfolio
        portfolio = await db.portfolio_create(
            userId=current_user.user_id,
            name="My Portfolio",
        )
    
    holdings = await db.holding_find_by_portfolio(portfolio.id)
    
    return {
        "id": portfolio.id,
        "userId": portfolio.userId,
        "name": portfolio.name,
        "description": portfolio.description,
        "isPublic": portfolio.isPublic,
        "holdings": [
            {
                "id": h.id,
                "symbol": h.symbol,
                "quantity": h.quantity,
                "purchasePrice": h.purchasePrice,
                "purchaseDate": h.purchaseDate.isoformat() if h.purchaseDate else None,
                "assetClass": h.assetClass,
            }
            for h in holdings
        ]
    }

@router.post("/import")
async def import_portfolio(
    holdings: List[HoldingImport],
    current_user: TokenData = Depends(get_current_user)
):
    """Import portfolio holdings"""
    # Get or create portfolio
    portfolio = await db.portfolio_find_by_user(current_user.user_id)
    
    if not portfolio:
        portfolio = await db.portfolio_create(
            userId=current_user.user_id,
            name="My Portfolio",
        )
    
    # Clear existing holdings
    await db.holding_delete_by_portfolio(portfolio.id)
    
    # Add new holdings
    for holding_data in holdings:
        await db.holding_create(
            portfolioId=portfolio.id,
            symbol=holding_data.symbol.upper(),
            quantity=holding_data.quantity,
            purchasePrice=holding_data.purchase_price,
            assetClass=holding_data.asset_class or "stock",
        )
    
    return {"success": True, "portfolioId": portfolio.id}
