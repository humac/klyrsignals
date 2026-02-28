"""
Test portfolio service
"""

import pytest
import asyncio
from app.models.holding import Holding
from app.services.portfolio_service import PortfolioService


@pytest.mark.asyncio
async def test_portfolio_analysis():
    """Test complete portfolio analysis"""
    holdings = [
        Holding(symbol="AAPL", quantity=50, purchase_price=150.00),
        Holding(symbol="MSFT", quantity=30, purchase_price=280.00),
    ]
    
    service = PortfolioService()
    analysis = await service.analyze(holdings)
    
    assert analysis.total_value > 0
    assert analysis.total_cost_basis > 0
    assert analysis.risk_score >= 0
    assert analysis.risk_score <= 100
    assert len(analysis.allocation) > 0
    assert len(analysis.sector_allocation) > 0


@pytest.mark.asyncio
async def test_portfolio_with_etf():
    """Test portfolio with mixed asset classes"""
    holdings = [
        Holding(symbol="AAPL", quantity=50, purchase_price=150.00, asset_class="stock"),
        Holding(symbol="VTI", quantity=100, purchase_price=220.00, asset_class="etf"),
    ]
    
    service = PortfolioService()
    analysis = await service.analyze(holdings)
    
    assert "stock" in analysis.allocation or "etf" in analysis.allocation
    assert analysis.total_value > 0


@pytest.mark.asyncio
async def test_portfolio_warnings():
    """Test that warnings are generated for concentrated portfolio"""
    holdings = [
        Holding(symbol="AAPL", quantity=100, purchase_price=150.00),
    ]
    
    service = PortfolioService()
    analysis = await service.analyze(holdings)
    
    # Single stock should generate warnings
    assert len(analysis.warnings) > 0


def test_holding_validation():
    """Test holding model validation"""
    # Valid holding
    holding = Holding(symbol="AAPL", quantity=50, purchase_price=150.00)
    assert holding.symbol == "AAPL"
    assert holding.quantity == 50
    
    # Invalid: negative quantity
    with pytest.raises(Exception):
        Holding(symbol="AAPL", quantity=-50, purchase_price=150.00)
    
    # Invalid: zero price
    with pytest.raises(Exception):
        Holding(symbol="AAPL", quantity=50, purchase_price=0)
