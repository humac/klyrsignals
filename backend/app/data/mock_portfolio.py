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
            "purchase_price": 145.00,
            "avg_cost": 145.00,  # Backward compatibility
            "price": 178.50,  # Current price alias
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
            "purchase_price": 280.00,
            "avg_cost": 280.00,  # Backward compatibility
            "price": 378.90,  # Current price alias
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
            "purchase_price": 95.00,
            "avg_cost": 95.00,  # Backward compatibility
            "price": 141.80,  # Current price alias
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
            "purchase_price": 125.00,
            "avg_cost": 125.00,  # Backward compatibility
            "price": 178.25,  # Current price alias
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
            "purchase_price": 420.00,
            "avg_cost": 420.00,  # Backward compatibility
            "price": 875.30,  # Current price alias
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
            "purchase_price": 140.00,
            "avg_cost": 140.00,  # Backward compatibility
            "price": 198.50,  # Current price alias
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
            "purchase_price": 160.00,
            "avg_cost": 160.00,  # Backward compatibility
            "price": 156.20,  # Current price alias
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
            "purchase_price": 95.00,
            "avg_cost": 95.00,  # Backward compatibility
            "price": 103.40,  # Current price alias
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
    "total_value": 250000.00,
    "total_cost_basis": 201250.00,
    "total_gain_loss": 48750.00,
    "total_gain_loss_pct": 24.38,
    "risk_score": 68,
    "risk_breakdown": {
        "concentration": 75,
        "volatility": 62,
        "correlation": 68
    },
    "allocation": {
        "Equity": 94.50,
        "Cash": 5.50
    },
    "sector_allocation": {
        "Technology": 65.22,
        "Financial Services": 9.53,
        "Healthcare": 6.25,
        "Energy": 6.20,
        "Consumer Cyclical": 12.83
    },
    "warnings": [
        {
            "type": "sector_concentration",
            "severity": "critical",
            "message": "Technology sector concentration (65.2%) exceeds recommended maximum (40%)",
            "details": {"current": 65.22, "recommended_max": 40.0},
            "affected_symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"]
        },
        {
            "type": "single_stock",
            "severity": "high",
            "message": "NVDA position (28.0%) exceeds recommended maximum (10%)",
            "details": {"current": 28.01, "recommended_max": 10.0},
            "affected_symbols": ["NVDA"]
        }
    ],
    "recommendations": [
        {
            "action": "sell",
            "symbol": "NVDA",
            "quantity": 50,
            "reason": "Reduce concentration risk from 28% to 10%",
            "priority": 1,
            "expected_impact": "Lower portfolio risk score by 15-20 points"
        },
        {
            "action": "buy",
            "symbol": "VTI",
            "quantity": 100,
            "reason": "Add broad market diversification",
            "priority": 2,
            "expected_impact": "Reduce single-stock risk exposure"
        },
        {
            "action": "buy",
            "symbol": "VXUS",
            "quantity": 150,
            "reason": "Add international equity exposure",
            "priority": 3,
            "expected_impact": "Improve geographic diversification"
        }
    ],
    "blind_spots": [
        {
            "type": "style_concentration",
            "confidence": 85,
            "message": "Growth-heavy portfolio with limited value exposure",
            "details": {"growth_pct": 78, "value_pct": 22},
            "affected_symbols": ["NVDA", "AMZN", "GOOGL"]
        },
        {
            "type": "geographic_concentration",
            "confidence": 92,
            "message": "No exposure to emerging markets",
            "details": {"developed_markets_pct": 94.5, "emerging_markets_pct": 0},
            "affected_symbols": []
        },
        {
            "type": "hidden_correlation",
            "confidence": 73,
            "message": "High correlation between tech holdings during market stress",
            "details": {"avg_correlation": 0.78},
            "affected_symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"]
        }
    ],
    "timestamp": "2026-02-28T23:24:00Z"
}
