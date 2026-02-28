"""
Test risk scoring algorithms
"""

import pytest
from app.models.holding import Holding
from app.core.scoring import calculate_risk_score, calculate_concentration_risk


def test_single_stock_concentration():
    """Test risk score with single stock (high concentration)"""
    holdings = [
        Holding(symbol="AAPL", quantity=100, purchase_price=150.00)
    ]
    prices = {"AAPL": 150.00}
    
    risk_score, breakdown = calculate_risk_score(holdings, prices)
    
    # Single stock should have high concentration risk
    assert risk_score > 50
    assert breakdown["concentration"] > 0


def test_diversified_portfolio():
    """Test risk score with diversified portfolio"""
    holdings = [
        Holding(symbol="AAPL", quantity=10, purchase_price=150.00, asset_class="stock"),
        Holding(symbol="MSFT", quantity=10, purchase_price=280.00, asset_class="stock"),
        Holding(symbol="VTI", quantity=20, purchase_price=220.00, asset_class="etf"),
        Holding(symbol="BND", quantity=30, purchase_price=75.00, asset_class="etf"),
    ]
    prices = {"AAPL": 150.00, "MSFT": 280.00, "VTI": 220.00, "BND": 75.00}
    
    risk_score, breakdown = calculate_risk_score(holdings, prices)
    
    # Diversified portfolio should have risk score in reasonable range
    # (ETFs count as "Broad Market" sector, reducing sector concentration)
    assert risk_score >= 0
    assert risk_score <= 100


def test_sector_concentration():
    """Test risk score with sector concentration"""
    holdings = [
        Holding(symbol="AAPL", quantity=50, purchase_price=150.00),
        Holding(symbol="MSFT", quantity=50, purchase_price=280.00),
        Holding(symbol="GOOGL", quantity=50, purchase_price=140.00),
    ]
    prices = {"AAPL": 150.00, "MSFT": 280.00, "GOOGL": 140.00}
    
    risk_score, breakdown = calculate_risk_score(holdings, prices)
    
    # All tech stocks should have high concentration risk
    assert breakdown["concentration"] > 30


def test_empty_portfolio():
    """Test risk score with empty portfolio"""
    holdings = []
    prices = {}
    
    risk_score, breakdown = calculate_risk_score(holdings, prices)
    
    assert risk_score == 0


def test_risk_score_range():
    """Test that risk score is always in valid range"""
    test_cases = [
        [Holding(symbol="AAPL", quantity=100, purchase_price=150.00)],
        [
            Holding(symbol="AAPL", quantity=10, purchase_price=150.00),
            Holding(symbol="MSFT", quantity=10, purchase_price=280.00),
        ],
    ]
    
    for holdings in test_cases:
        prices = {h.symbol: h.purchase_price for h in holdings}
        risk_score, _ = calculate_risk_score(holdings, prices)
        
        assert 0 <= risk_score <= 100
