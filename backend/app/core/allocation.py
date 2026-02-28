"""
Allocation calculations - Portfolio allocation by category
"""

from app.models.holding import Holding
from typing import Optional


# Sector mapping for common tickers (simplified for v1.0)
SECTOR_MAP = {
    # Technology
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'GOOGL': 'Technology',
    'GOOG': 'Technology',
    'META': 'Technology',
    'NVDA': 'Technology',
    'ADBE': 'Technology',
    'CRM': 'Technology',
    'ORCL': 'Technology',
    'INTC': 'Technology',
    'AMD': 'Technology',
    'CSCO': 'Technology',
    'AVGO': 'Technology',
    'TXN': 'Technology',
    'QCOM': 'Technology',
    
    # Healthcare
    'JNJ': 'Healthcare',
    'UNH': 'Healthcare',
    'PFE': 'Healthcare',
    'MRK': 'Healthcare',
    'ABBV': 'Healthcare',
    'TMO': 'Healthcare',
    'ABT': 'Healthcare',
    'DHR': 'Healthcare',
    'BMY': 'Healthcare',
    'LLY': 'Healthcare',
    
    # Financial
    'JPM': 'Financial',
    'BAC': 'Financial',
    'WFC': 'Financial',
    'GS': 'Financial',
    'MS': 'Financial',
    'C': 'Financial',
    'AXP': 'Financial',
    'BLK': 'Financial',
    'SCHW': 'Financial',
    'USB': 'Financial',
    
    # Consumer
    'AMZN': 'Consumer',
    'TSLA': 'Consumer',
    'HD': 'Consumer',
    'NKE': 'Consumer',
    'MCD': 'Consumer',
    'SBUX': 'Consumer',
    'LOW': 'Consumer',
    'TGT': 'Consumer',
    'COST': 'Consumer',
    'WMT': 'Consumer',
    
    # Energy
    'XOM': 'Energy',
    'CVX': 'Energy',
    'COP': 'Energy',
    'SLB': 'Energy',
    'EOG': 'Energy',
    'MPC': 'Energy',
    'PSX': 'Energy',
    'VLO': 'Energy',
    
    # Industrial
    'CAT': 'Industrial',
    'BA': 'Industrial',
    'HON': 'Industrial',
    'UPS': 'Industrial',
    'GE': 'Industrial',
    'MMM': 'Industrial',
    'LMT': 'Industrial',
    'RTX': 'Industrial',
    
    # Communication
    'NFLX': 'Communication',
    'DIS': 'Communication',
    'CMCSA': 'Communication',
    'VZ': 'Communication',
    'T': 'Communication',
    'TMUS': 'Communication',
    
    # Utilities
    'NEE': 'Utilities',
    'DUK': 'Utilities',
    'SO': 'Utilities',
    'D': 'Utilities',
    'AEP': 'Utilities',
    'EXC': 'Utilities',
    
    # Real Estate
    'AMT': 'Real Estate',
    'PLD': 'Real Estate',
    'CCI': 'Real Estate',
    'EQIX': 'Real Estate',
    'SPG': 'Real Estate',
    
    # Materials
    'LIN': 'Materials',
    'APD': 'Materials',
    'ECL': 'Materials',
    'SHW': 'Materials',
    'FCX': 'Materials',
    'NEM': 'Materials',
}

# ETF sector mappings (simplified)
ETF_SECTOR_MAP = {
    'QQQ': 'Technology',
    'XLK': 'Technology',
    'XLF': 'Financial',
    'XLV': 'Healthcare',
    'XLE': 'Energy',
    'XLI': 'Industrial',
    'XLP': 'Consumer',
    'XLY': 'Consumer',
    'XLU': 'Utilities',
    'XLRE': 'Real Estate',
    'XLB': 'Materials',
    'XLC': 'Communication',
}


def get_sector(symbol: str, asset_class: str = "stock") -> Optional[str]:
    """
    Get sector for a given symbol.
    
    Args:
        symbol: Ticker symbol
        asset_class: Asset class (stock, etf, etc.)
        
    Returns:
        Sector name or None if not found
    """
    symbol_upper = symbol.upper()
    
    # Check ETF map first
    if symbol_upper in ETF_SECTOR_MAP:
        return ETF_SECTOR_MAP[symbol_upper]
    
    # Check stock sector map
    if symbol_upper in SECTOR_MAP:
        return SECTOR_MAP[symbol_upper]
    
    # For ETFs, return based on asset class
    if asset_class == "etf":
        return "Broad Market"
    
    # For crypto
    if asset_class == "crypto":
        return "Cryptocurrency"
    
    # Unknown
    return "Other"


def calculate_allocation(
    holdings: list[Holding],
    prices: dict[str, float]
) -> tuple[dict[str, float], dict[str, float]]:
    """
    Calculate portfolio allocation by asset class and sector.
    
    Args:
        holdings: List of holdings
        prices: Current prices for each symbol
        
    Returns:
        Tuple of (asset_class_allocation, sector_allocation) as percentages
    """
    # Calculate value for each holding
    holding_values = []
    for holding in holdings:
        price = prices.get(holding.symbol, holding.purchase_price)
        value = holding.quantity * price
        sector = get_sector(holding.symbol, holding.asset_class)
        holding_values.append({
            'symbol': holding.symbol,
            'value': value,
            'asset_class': holding.asset_class,
            'sector': sector or 'Other',
        })
    
    total_value = sum(h['value'] for h in holding_values)
    if total_value == 0:
        return {}, {}
    
    # Calculate asset class allocation
    asset_class_totals = {}
    for h in holding_values:
        ac = h['asset_class']
        asset_class_totals[ac] = asset_class_totals.get(ac, 0) + h['value']
    
    asset_class_allocation = {
        ac: round((value / total_value) * 100, 2)
        for ac, value in asset_class_totals.items()
    }
    
    # Calculate sector allocation
    sector_totals = {}
    for h in holding_values:
        sector = h['sector']
        sector_totals[sector] = sector_totals.get(sector, 0) + h['value']
    
    sector_allocation = {
        sector: round((value / total_value) * 100, 2)
        for sector, value in sector_totals.items()
    }
    
    return asset_class_allocation, sector_allocation
