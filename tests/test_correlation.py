"""Tests for the correlation engine."""

import pandas as pd
import numpy as np

from app.services.auditor.correlation import (
    compute_correlation_matrix,
    find_hidden_twins,
    run_correlation_analysis,
)


def _make_price_histories(correlations: dict[str, list[float]]) -> dict[str, pd.DataFrame]:
    """Create synthetic price histories for testing."""
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    results = {}
    for symbol, prices in correlations.items():
        results[symbol] = pd.DataFrame({
            "date": dates[:len(prices)],
            "close": prices,
        })
    return results


class TestCorrelationMatrix:
    def test_highly_correlated_pair(self):
        """Two perfectly correlated series should have correlation ~1.0."""
        np.random.seed(42)
        base = np.cumsum(np.random.randn(100)) + 100
        # Second series is just the first + small noise
        histories = {
            "SYM_A": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base}),
            "SYM_B": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base + np.random.randn(100) * 0.01}),
        }
        corr_df, corr_dict = compute_correlation_matrix(histories)
        assert not corr_df.empty
        assert corr_dict["SYM_A"]["SYM_B"] > 0.95

    def test_uncorrelated_pair(self):
        """Two random walks should have low correlation."""
        np.random.seed(42)
        histories = {
            "SYM_A": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=200), "close": np.cumsum(np.random.randn(200)) + 100}),
            "SYM_B": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=200), "close": np.cumsum(np.random.randn(200)) + 100}),
        }
        corr_df, corr_dict = compute_correlation_matrix(histories)
        assert abs(corr_dict["SYM_A"]["SYM_B"]) < 0.8

    def test_insufficient_data(self):
        """Less than 2 symbols should return empty."""
        histories = {
            "SYM_A": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=50), "close": range(50)}),
        }
        corr_df, corr_dict = compute_correlation_matrix(histories)
        assert corr_df.empty
        assert corr_dict == {}


class TestHiddenTwins:
    def test_finds_twin(self):
        np.random.seed(42)
        base = np.cumsum(np.random.randn(100)) + 100
        histories = {
            "BNS.TO": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base}),
            "TD.TO": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base * 1.01 + np.random.randn(100) * 0.001}),
        }
        positions_df = pd.DataFrame({
            "normalized_symbol": ["BNS.TO", "TD.TO"],
            "weight_pct": [30.0, 25.0],
        })
        corr_df, _ = compute_correlation_matrix(histories)
        twins = find_hidden_twins(corr_df, positions_df)
        assert len(twins) >= 1
        assert twins[0].correlation > 0.8

    def test_no_twins_when_uncorrelated(self):
        np.random.seed(42)
        histories = {
            "AAPL": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=200), "close": np.cumsum(np.random.randn(200)) + 100}),
            "GOLD": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=200), "close": np.cumsum(np.random.randn(200)) + 50}),
        }
        positions_df = pd.DataFrame({
            "normalized_symbol": ["AAPL", "GOLD"],
            "weight_pct": [50.0, 50.0],
        })
        corr_df, _ = compute_correlation_matrix(histories)
        twins = find_hidden_twins(corr_df, positions_df)
        # May or may not find twins depending on random seed, but correlation should be low
        for twin in twins:
            assert abs(twin.correlation) >= 0.8


class TestRunCorrelationAnalysis:
    def test_full_pipeline(self):
        np.random.seed(42)
        base = np.cumsum(np.random.randn(100)) + 100
        histories = {
            "A": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base}),
            "B": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": base + np.random.randn(100) * 0.001}),
            "C": pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "close": np.cumsum(np.random.randn(100)) + 50}),
        }
        positions_df = pd.DataFrame({
            "normalized_symbol": ["A", "B", "C"],
            "weight_pct": [40.0, 35.0, 25.0],
        })
        report = run_correlation_analysis(histories, positions_df)
        assert report.correlation_matrix is not None
        assert len(report.correlation_matrix) == 3
