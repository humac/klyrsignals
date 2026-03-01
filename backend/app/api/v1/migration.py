"""
Migration API - Migrate localStorage portfolio data to cloud database
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.auth import get_current_user, TokenData
from app.services.database import db
from app.services.portfolio_service import PortfolioService

router = APIRouter()


class HoldingMigration(BaseModel):
    """Holding data from localStorage"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Price per share at purchase")
    purchase_date: Optional[str] = Field(None, description="Date of purchase (ISO format)")
    asset_class: Optional[str] = Field("stock", description="Asset class")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not v or not v.strip():
            raise ValueError("Symbol cannot be empty")
        return v.strip().upper()
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    @validator('purchase_price')
    def validate_purchase_price(cls, v):
        """Validate purchase price is positive"""
        if v <= 0:
            raise ValueError("Purchase price must be positive")
        return v
    
    @validator('asset_class')
    def validate_asset_class(cls, v):
        """Validate asset class"""
        valid_classes = ["stock", "etf", "crypto", "mutual_fund"]
        if v and v not in valid_classes:
            return "stock"  # Default to stock if invalid
        return v or "stock"


class MigrationRequest(BaseModel):
    """Migration request body"""
    holdings: List[HoldingMigration] = Field(..., min_length=1, description="Holdings to migrate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MigrationResponse(BaseModel):
    """Migration response"""
    success: bool
    portfolio_id: str
    holdings_migrated: int
    holdings_failed: int = 0
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@router.post("/", response_model=MigrationResponse)
async def migrate_portfolio(
    request: MigrationRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Migrate localStorage portfolio data to cloud database.
    
    This endpoint accepts portfolio data from localStorage and saves it to the user's
    portfolio in the database. It handles validation, duplicate symbols, and audit logging.
    """
    try:
        # Validate holdings count
        if not request.holdings or len(request.holdings) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No holdings provided for migration"
            )
        
        # Get or create user's portfolio
        portfolio = await db.portfolio_find_by_user(current_user.user_id)
        
        if not portfolio:
            portfolio = await db.portfolio_create(
                userId=current_user.user_id,
                name="Migrated Portfolio",
                description="Imported from localStorage"
            )
        
        # Clear existing holdings (fresh migration)
        await db.holding_delete_by_portfolio(portfolio.id)
        
        # Track migration stats
        holdings_migrated = 0
        holdings_failed = 0
        failed_symbols = []
        
        # Process each holding with duplicate handling
        symbol_map = {}  # Track symbols for merging
        
        for holding_data in request.holdings:
            try:
                symbol = holding_data.symbol.upper()
                
                # Handle duplicate symbols by merging quantities
                if symbol in symbol_map:
                    # Merge: add quantities, recalculate average price
                    existing = symbol_map[symbol]
                    total_qty = existing['quantity'] + holding_data.quantity
                    total_cost = (existing['quantity'] * existing['purchase_price']) + \
                                (holding_data.quantity * holding_data.purchase_price)
                    avg_price = total_cost / total_qty if total_qty > 0 else holding_data.purchase_price
                    
                    symbol_map[symbol] = {
                        'quantity': total_qty,
                        'purchase_price': avg_price,
                        'asset_class': holding_data.asset_class or existing['asset_class'],
                        'purchase_date': holding_data.purchase_date or existing['purchase_date']
                    }
                else:
                    symbol_map[symbol] = {
                        'quantity': holding_data.quantity,
                        'purchase_price': holding_data.purchase_price,
                        'asset_class': holding_data.asset_class or "stock",
                        'purchase_date': holding_data.purchase_date
                    }
            except Exception as e:
                holdings_failed += 1
                failed_symbols.append(holding_data.symbol)
                continue
        
        # Save merged holdings to database
        for symbol, data in symbol_map.items():
            try:
                await db.holding_create(
                    portfolioId=portfolio.id,
                    symbol=symbol,
                    quantity=data['quantity'],
                    purchasePrice=data['purchase_price'],
                    assetClass=data['asset_class'],
                )
                holdings_migrated += 1
            except Exception as e:
                holdings_failed += 1
                failed_symbols.append(symbol)
        
        # Log migration to audit log
        await db.audit_log_create(
            userId=current_user.user_id,
            action="portfolio_migration",
            details={
                "holdings_count": holdings_migrated,
                "failed_count": holdings_failed,
                "failed_symbols": failed_symbols,
                "source": "localStorage",
                "portfolio_id": portfolio.id
            }
        )
        
        # Build response message
        if holdings_failed > 0:
            message = f"Migration completed with {holdings_migrated} holdings migrated, {holdings_failed} failed"
        else:
            message = f"Successfully migrated {holdings_migrated} holdings to cloud portfolio"
        
        return MigrationResponse(
            success=holdings_failed == 0,
            portfolio_id=portfolio.id,
            holdings_migrated=holdings_migrated,
            holdings_failed=holdings_failed,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/status")
async def get_migration_status(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Check if user has localStorage data to migrate.
    
    This is a helper endpoint for the frontend to determine
    if the migration prompt should be shown.
    """
    # Check if user has a portfolio with holdings
    portfolio = await db.portfolio_find_by_user(current_user.user_id)
    
    if not portfolio:
        return {
            "has_cloud_portfolio": False,
            "holdings_count": 0,
            "needs_migration_check": True
        }
    
    holdings = await db.holding_find_by_portfolio(portfolio.id)
    
    return {
        "has_cloud_portfolio": True,
        "holdings_count": len(holdings),
        "portfolio_id": portfolio.id,
        "needs_migration_check": len(holdings) == 0
    }
