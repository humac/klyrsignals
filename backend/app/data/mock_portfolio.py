"""
Mock Portfolio Data for KlyrSignals Demo/Screenshots

This module provides realistic portfolio data for:
- Demo purposes
- Screenshot generation
- Testing without real market data
"""

MOCK_PORTFOLIO = {
    "portfolio_id": "demo-001",
    "name": "Demo Portfolio",
    "total_value": 250000.00,
    "cash": 12500.00,
    "holdings": [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 150,
            "avg_cost": 145.00,
            "current_price": 178.50,
            "market_value": 26775.00,
            "weight": 10.71,
            "sector": "Technology",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "quantity": 100,
            "avg_cost": 280.00,
            "current_price": 378.90,
            "market_value": 37890.00,
            "weight": 15.16,
            "sector": "Technology",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "quantity": 200,
            "avg_cost": 95.00,
            "current_price": 141.80,
            "market_value": 28360.00,
            "weight": 11.34,
            "sector": "Technology",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "AMZN",
            "name": "Amazon.com Inc.",
            "quantity": 180,
            "avg_cost": 125.00,
            "current_price": 178.25,
            "market_value": 32085.00,
            "weight": 12.83,
            "sector": "Consumer Cyclical",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "NVDA",
            "name": "NVIDIA Corporation",
            "quantity": 80,
            "avg_cost": 420.00,
            "current_price": 875.30,
            "market_value": 70024.00,
            "weight": 28.01,
            "sector": "Technology",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "JPM",
            "name": "JPMorgan Chase & Co.",
            "quantity": 120,
            "avg_cost": 140.00,
            "current_price": 198.50,
            "market_value": 23820.00,
            "weight": 9.53,
            "sector": "Financial Services",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "JNJ",
            "name": "Johnson & Johnson",
            "quantity": 100,
            "avg_cost": 160.00,
            "current_price": 156.20,
            "market_value": 15620.00,
            "weight": 6.25,
            "sector": "Healthcare",
            "asset_class": "Equity",
            "geography": "North America"
        },
        {
            "symbol": "XOM",
            "name": "Exxon Mobil Corporation",
            "quantity": 150,
            "avg_cost": 95.00,
            "current_price": 103.40,
            "market_value": 15510.00,
            "weight": 6.20,
            "sector": "Energy",
            "asset_class": "Equity",
            "geography": "North America"
        }
    ],
    "performance": {
        "total_return": 48750.00,
        "total_return_pct": 24.38,
        "day_change": 2150.00,
        "day_change_pct": 0.87,
        "ytd_return_pct": 8.45
    }
}

MOCK_ANALYSIS = {
    "risk_score": 68,
    "risk_level": "Moderate-High",
    "allocation": {
        "by_sector": {
            "Technology": 65.22,
            "Financial Services": 9.53,
            "Healthcare": 6.25,
            "Energy": 6.20,
            "Consumer Cyclical": 12.83
        },
        "by_asset_class": {
            "Equity": 94.50,
            "Cash": 5.50
        },
        "by_geography": {
            "North America": 94.50,
            "Cash": 5.50
        }
    },
    "blind_spots": [
        {
            "type": "sector_concentration",
            "severity": "high",
            "title": "Heavy Technology Concentration",
            "description": "65.2% of portfolio in Technology sector (recommended max: 40%)",
            "recommendation": "Consider diversifying into Healthcare, Consumer Defensive, or Utilities"
        },
        {
            "type": "single_stock_risk",
            "severity": "medium",
            "title": "Large Position in NVDA",
            "description": "NVIDIA represents 28.0% of portfolio (recommended max: 10%)",
            "recommendation": "Consider reducing NVDA position to 10-15% and reallocating"
        },
        {
            "type": "geographic_concentration",
            "severity": "medium",
            "title": "US-Only Exposure",
            "description": "94.5% of equity holdings in North America only",
            "recommendation": "Add international developed markets (Europe, Asia) for diversification"
        }
    ],
    "over_exposure": [
        {
            "category": "Sector",
            "name": "Technology",
            "current": 65.22,
            "recommended_max": 40.0,
            "excess": 25.22,
            "severity": "critical"
        },
        {
            "category": "Single Stock",
            "name": "NVDA",
            "current": 28.01,
            "recommended_max": 10.0,
            "excess": 18.01,
            "severity": "high"
        }
    ],
    "rebalancing": [
        {
            "action": "sell",
            "symbol": "NVDA",
            "current_shares": 80,
            "recommended_shares": 30,
            "shares_to_trade": -50,
            "estimated_proceeds": 43765.00,
            "reason": "Reduce concentration risk from 28% to 10%"
        },
        {
            "action": "buy",
            "symbol": "VTI",
            "recommended_shares": 100,
            "estimated_cost": 24500.00,
            "reason": "Add broad market diversification"
        },
        {
            "action": "buy",
            "symbol": "VXUS",
            "recommended_shares": 150,
            "estimated_cost": 13500.00,
            "reason": "Add international equity exposure"
        }
    ]
}
