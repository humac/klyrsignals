"""
Risk scoring algorithms
"""

from app.models.holding import Holding
from app.core.allocation import calculate_allocation
from typing import Optional


def calculate_concentration_risk(
    asset_class_allocation: dict[str, float],
    sector_allocation: dict[str, float],
    holdings: list[Holding],
    prices: dict[str, float]
) -> int:
    """
    Calculate concentration risk score (0-50 points).
    
    Scoring:
    - Single stock >20%: +20 points
    - Single stock >10%: +10 points
    - Sector >40%: +20 points
    - Sector >25%: +10 points
    - Asset class >80%: +10 points
    
    Args:
        asset_class_allocation: Allocation by asset class (%)
        sector_allocation: Allocation by sector (%)
        holdings: List of holdings
        prices: Current prices
        
    Returns:
        Concentration risk score (0-50)
    """
    score = 0
    
    # Calculate total portfolio value
    total_value = sum(
        h.quantity * prices.get(h.symbol, h.purchase_price)
        for h in holdings
    )
    
    if total_value == 0:
        return 0
    
    # Check single stock concentration
    for holding in holdings:
        value = holding.quantity * prices.get(holding.symbol, holding.purchase_price)
        pct = (value / total_value) * 100
        
        if pct > 20:
            score += 20
        elif pct > 10:
            score += 10
    
    # Check sector concentration
    for sector, pct in sector_allocation.items():
        if pct > 40:
            score += 20
        elif pct > 25:
            score += 10
    
    # Check asset class concentration
    for asset_class, pct in asset_class_allocation.items():
        if pct > 80:
            score += 10
    
    return min(50, score)


def calculate_volatility_risk(
    holdings: list[Holding],
    prices: dict[str, float]
) -> int:
    """
    Calculate volatility risk score (0-30 points).
    
    Simplified for v1.0 (no historical data):
    - Crypto holdings >50%: +15 points
    - Single stock >15%: +8 points
    - Tech sector >60%: +7 points
    
    Args:
        holdings: List of holdings
        prices: Current prices
        
    Returns:
        Volatility risk score (0-30)
    """
    score = 0
    
    # Calculate total value
    total_value = sum(
        h.quantity * prices.get(h.symbol, h.purchase_price)
        for h in holdings
    )
    
    if total_value == 0:
        return 0
    
    # Check crypto exposure
    crypto_value = sum(
        h.quantity * prices.get(h.symbol, h.purchase_price)
        for h in holdings if h.asset_class == 'crypto'
    )
    crypto_pct = (crypto_value / total_value) * 100
    if crypto_pct > 50:
        score += 15
    
    # Check single stock volatility
    for holding in holdings:
        value = holding.quantity * prices.get(holding.symbol, holding.purchase_price)
        pct = (value / total_value) * 100
        if pct > 15:
            score += 8
            break
    
    # Check tech sector concentration (proxy for volatility)
    from app.core.allocation import get_sector
    tech_value = sum(
        h.quantity * prices.get(h.symbol, h.purchase_price)
        for h in holdings
        if get_sector(h.symbol, h.asset_class) == 'Technology'
    )
    tech_pct = (tech_value / total_value) * 100
    if tech_pct > 60:
        score += 7
    
    return min(30, score)


def calculate_correlation_risk(
    holdings: list[Holding],
    sector_allocation: dict[str, float]
) -> int:
    """
    Calculate correlation risk score (0-20 points).
    
    Simplified for v1.0 (sector-based proxy):
    - Single sector >50%: +20 points
    - Single sector >35%: +10 points
    - Top 2 sectors >70%: +5 points
    
    Args:
        holdings: List of holdings
        sector_allocation: Allocation by sector (%)
        
    Returns:
        Correlation risk score (0-20)
    """
    score = 0
    
    # Check single sector dominance
    max_sector_pct = max(sector_allocation.values()) if sector_allocation else 0
    
    if max_sector_pct > 50:
        score += 20
    elif max_sector_pct > 35:
        score += 10
    
    # Check top 2 sectors concentration
    if len(sector_allocation) >= 2:
        sorted_sectors = sorted(sector_allocation.values(), reverse=True)
        top_2_pct = sorted_sectors[0] + sorted_sectors[1]
        if top_2_pct > 70:
            score += 5
    
    return min(20, score)


def calculate_risk_score(
    holdings: list[Holding],
    prices: dict[str, float]
) -> tuple[int, dict[str, int]]:
    """
    Calculate composite risk score (0-100).
    
    Risk Score = Concentration Risk (50%) + Volatility Risk (30%) + Correlation Risk (20%)
    
    Args:
        holdings: List of holdings
        prices: Current prices
        
    Returns:
        Tuple of (total_risk_score, risk_breakdown)
    """
    from app.core.allocation import calculate_allocation
    
    # Calculate allocations
    asset_class_allocation, sector_allocation = calculate_allocation(holdings, prices)
    
    # Calculate component scores
    concentration_risk = calculate_concentration_risk(
        asset_class_allocation, sector_allocation, holdings, prices
    )
    volatility_risk = calculate_volatility_risk(holdings, prices)
    correlation_risk = calculate_correlation_risk(holdings, sector_allocation)
    
    # Calculate total
    total_risk = concentration_risk + volatility_risk + correlation_risk
    
    risk_breakdown = {
        "concentration": concentration_risk,
        "volatility": volatility_risk,
        "correlation": correlation_risk,
    }
    
    return min(100, total_risk), risk_breakdown
