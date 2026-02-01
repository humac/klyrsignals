"""Tests for the concentration auditor."""

import pandas as pd

from app.services.auditor.concentration import run_concentration_audit


def _make_positions_df(holdings: list[dict]) -> pd.DataFrame:
    """Helper to create a positions DataFrame."""
    df = pd.DataFrame(holdings)
    total = df["market_value_cents"].sum()
    if total > 0:
        df["weight_pct"] = round(df["market_value_cents"] / total * 100, 2)
    else:
        df["weight_pct"] = 0.0
    return df


class TestConcentrationAudit:
    def test_empty_portfolio(self):
        report = run_concentration_audit(pd.DataFrame(), {})
        assert report.alerts == []
        assert report.home_bias_pct == 0.0

    def test_home_bias_warning(self):
        df = _make_positions_df([
            {"normalized_symbol": "XIC.TO", "market_value_cents": 70000_00, "symbol": "XIC"},
            {"normalized_symbol": "VFV.TO", "market_value_cents": 30000_00, "symbol": "VFV"},
        ])
        weights = {
            "XIC.TO": {"sectors": {"Financials": 35, "Energy": 16, "Other": 49}, "countries": {"CAN": 100}},
            "VFV.TO": {"sectors": {"Technology": 29, "Other": 71}, "countries": {"USA": 100}},
        }
        report = run_concentration_audit(df, weights)
        assert report.home_bias_pct == 70.0

        home_bias_alerts = [a for a in report.alerts if a.category == "home_bias"]
        assert len(home_bias_alerts) == 1
        assert home_bias_alerts[0].severity == "warning"

    def test_sector_concentration_warning(self):
        df = _make_positions_df([
            {"normalized_symbol": "BNS.TO", "market_value_cents": 50000_00, "symbol": "BNS"},
            {"normalized_symbol": "TD.TO", "market_value_cents": 50000_00, "symbol": "TD"},
        ])
        weights = {
            "BNS.TO": {"sectors": {"Financials": 100}, "countries": {"CAN": 100}},
            "TD.TO": {"sectors": {"Financials": 100}, "countries": {"CAN": 100}},
        }
        report = run_concentration_audit(df, weights)

        assert report.sector_weights["Financials"] == 100.0
        sector_alerts = [a for a in report.alerts if a.category == "sector"]
        assert len(sector_alerts) >= 1
        assert sector_alerts[0].severity == "critical"

    def test_no_alerts_diversified(self):
        df = _make_positions_df([
            {"normalized_symbol": "VEQT.TO", "market_value_cents": 100000_00, "symbol": "VEQT"},
        ])
        weights = {
            "VEQT.TO": {
                "sectors": {"Financials": 19.5, "Technology": 18, "Industrials": 11.5,
                            "Healthcare": 10.5, "Consumer Discretionary": 9.5,
                            "Energy": 6.0, "Materials": 5.0, "Utilities": 3.5,
                            "Real Estate": 3.5, "Communication Services": 6.0,
                            "Consumer Staples": 7.0},
                "countries": {"USA": 44, "CAN": 30, "JPN": 5.5, "OTHER": 20.5},
            },
        }
        report = run_concentration_audit(df, weights)

        # No individual named sector should exceed 25%
        sector_alerts = [a for a in report.alerts if a.category == "sector"]
        assert len(sector_alerts) == 0

    def test_single_holding_warning(self):
        df = _make_positions_df([
            {"normalized_symbol": "SHOP.TO", "market_value_cents": 80000_00, "symbol": "SHOP"},
            {"normalized_symbol": "VFV.TO", "market_value_cents": 20000_00, "symbol": "VFV"},
        ])
        weights = {
            "SHOP.TO": {"sectors": {"Technology": 100}, "countries": {"CAN": 100}},
            "VFV.TO": {"sectors": {"Technology": 29, "Other": 71}, "countries": {"USA": 100}},
        }
        report = run_concentration_audit(df, weights)
        single_alerts = [a for a in report.alerts if a.category == "single_holding"]
        assert len(single_alerts) >= 1
