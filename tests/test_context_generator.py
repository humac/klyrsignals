"""Tests for the AI context generator."""

import pandas as pd

from app.schemas.analysis import ConcentrationReport, ConcentrationAlert, CorrelationReport, HiddenTwin
from app.services.ai.context_generator import build_analysis_prompt


class TestContextGenerator:
    def test_builds_prompt_with_data(self):
        df = pd.DataFrame({
            "symbol": ["VGRO", "XIC", "BNS"],
            "normalized_symbol": ["VGRO.TO", "XIC.TO", "BNS.TO"],
            "description": ["Vanguard Growth ETF", "iShares Core S&P/TSX", "Bank of Nova Scotia"],
            "asset_class": ["equity", "equity", "equity"],
            "units": [100.0, 200.0, 50.0],
            "cost_basis_cents": [2500_00, 5000_00, 3500_00],
            "market_value_cents": [3000_00, 5500_00, 4000_00],
            "currency": ["CAD", "CAD", "CAD"],
            "exchange": ["TSX", "TSX", "TSX"],
            "last_price_cents": [30_00, 27_50, 80_00],
            "account_name": ["TFSA", "TFSA", "RRSP"],
            "account_type": ["TFSA", "TFSA", "RRSP"],
            "gain_loss_cents": [500_00, 500_00, 500_00],
            "gain_loss_pct": [20.0, 10.0, 14.3],
            "weight_pct": [24.0, 44.0, 32.0],
        })

        concentration = ConcentrationReport(
            alerts=[
                ConcentrationAlert(
                    category="sector", name="Financials", weight_pct=35.0,
                    threshold_pct=25.0, severity="warning",
                ),
            ],
            sector_weights={"Financials": 35.0, "Technology": 15.0, "Other": 50.0},
            country_weights={"CAN": 65.0, "USA": 25.0, "OTHER": 10.0},
            home_bias_pct=65.0,
        )

        correlation = CorrelationReport(
            hidden_twins=[
                HiddenTwin(
                    symbol_a="XIC.TO", symbol_b="BNS.TO",
                    correlation=0.85,
                    explanation="Highly correlated Canadian financials",
                ),
            ],
            correlation_matrix={},
        )

        system_prompt, user_prompt = build_analysis_prompt(df, concentration, correlation)

        assert "KlyrSignals" in system_prompt
        assert "VGRO" in user_prompt
        assert "BNS" in user_prompt
        assert "Financials" in user_prompt
        assert "Home Bias" in user_prompt
        assert "HIDDEN TWINS" in user_prompt
        assert "$12,500.00" in user_prompt  # Total value

    def test_empty_portfolio(self):
        df = pd.DataFrame()
        concentration = ConcentrationReport(
            alerts=[], sector_weights={}, country_weights={}, home_bias_pct=0.0,
        )
        correlation = CorrelationReport(hidden_twins=[], correlation_matrix={})

        system_prompt, user_prompt = build_analysis_prompt(df, concentration, correlation)
        assert "No holdings data" in user_prompt

    def test_prompt_contains_signal_format_instructions(self):
        df = pd.DataFrame({
            "symbol": ["AAPL"],
            "normalized_symbol": ["AAPL"],
            "description": ["Apple Inc"],
            "asset_class": ["equity"],
            "units": [10.0],
            "cost_basis_cents": [150000],
            "market_value_cents": [180000],
            "currency": ["USD"],
            "exchange": ["NASDAQ"],
            "last_price_cents": [18000],
            "account_name": ["TFSA"],
            "account_type": ["TFSA"],
            "gain_loss_cents": [30000],
            "gain_loss_pct": [20.0],
            "weight_pct": [100.0],
        })

        concentration = ConcentrationReport(
            alerts=[], sector_weights={}, country_weights={}, home_bias_pct=0.0,
        )
        correlation = CorrelationReport(hidden_twins=[], correlation_matrix={})

        system_prompt, _ = build_analysis_prompt(df, concentration, correlation)
        assert "signal_id" in system_prompt
        assert "JSON" in system_prompt
        assert "severity" in system_prompt
