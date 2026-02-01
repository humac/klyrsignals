"""Correlation Engine: detect 'Hidden Twins' and diversification blind spots.

Uses 36-month trailing price history to compute pairwise correlations.
Flags pairs with correlation > 0.8 as hidden twins.
"""

import pandas as pd
import numpy as np
import structlog

from app.schemas.analysis import HiddenTwin, CorrelationReport

logger = structlog.get_logger()

HIDDEN_TWIN_THRESHOLD = 0.80


def compute_correlation_matrix(
    price_histories: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    """Compute the pairwise correlation matrix from price histories.

    Args:
        price_histories: Dict of {symbol: DataFrame with 'date' and 'close' columns}

    Returns:
        (correlation_df, correlation_dict) where correlation_dict is JSON-serializable
    """
    if len(price_histories) < 2:
        return pd.DataFrame(), {}

    # Build a combined returns DataFrame
    returns_data = {}

    for symbol, df in price_histories.items():
        if df.empty or len(df) < 20:
            continue

        # Sort by date and compute daily returns
        series = df.sort_values("date").set_index("date")["close"]
        daily_returns = series.pct_change().dropna()

        if len(daily_returns) >= 20:
            returns_data[symbol] = daily_returns

    if len(returns_data) < 2:
        return pd.DataFrame(), {}

    # Align all series to common dates
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()

    if len(returns_df) < 20:
        return pd.DataFrame(), {}

    # Compute correlation matrix
    corr_matrix = returns_df.corr()

    # Convert to serializable dict
    corr_dict = {}
    for col in corr_matrix.columns:
        corr_dict[col] = {
            row: round(float(corr_matrix.loc[row, col]), 4)
            for row in corr_matrix.index
        }

    return corr_matrix, corr_dict


def find_hidden_twins(
    corr_matrix: pd.DataFrame,
    positions_df: pd.DataFrame,
    threshold: float = HIDDEN_TWIN_THRESHOLD,
) -> list[HiddenTwin]:
    """Identify pairs of holdings with dangerously high correlation.

    These are 'hidden twins' — assets that appear different but move together,
    giving a false sense of diversification.
    """
    if corr_matrix.empty:
        return []

    twins = []
    seen_pairs = set()
    symbols = corr_matrix.columns.tolist()

    for i, sym_a in enumerate(symbols):
        for j, sym_b in enumerate(symbols):
            if i >= j:
                continue

            pair_key = tuple(sorted([sym_a, sym_b]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            corr_val = float(corr_matrix.loc[sym_a, sym_b])
            if abs(corr_val) >= threshold:
                explanation = _generate_twin_explanation(
                    sym_a, sym_b, corr_val, positions_df
                )
                twins.append(HiddenTwin(
                    symbol_a=sym_a,
                    symbol_b=sym_b,
                    correlation=round(corr_val, 4),
                    explanation=explanation,
                ))

    twins.sort(key=lambda t: abs(t.correlation), reverse=True)

    logger.info("hidden_twins_found", count=len(twins), threshold=threshold)
    return twins


def run_correlation_analysis(
    price_histories: dict[str, pd.DataFrame],
    positions_df: pd.DataFrame,
) -> CorrelationReport:
    """Full correlation analysis pipeline."""
    corr_matrix, corr_dict = compute_correlation_matrix(price_histories)
    twins = find_hidden_twins(corr_matrix, positions_df)

    return CorrelationReport(
        hidden_twins=twins,
        correlation_matrix=corr_dict,
    )


def _generate_twin_explanation(
    sym_a: str, sym_b: str, correlation: float, positions_df: pd.DataFrame
) -> str:
    """Generate a human-readable explanation of why two holdings are twins."""
    direction = "positively" if correlation > 0 else "negatively"
    strength = "very strongly" if abs(correlation) >= 0.95 else "strongly"

    # Find the holdings in the positions DataFrame
    weight_a = 0.0
    weight_b = 0.0
    if not positions_df.empty:
        mask_a = positions_df["normalized_symbol"] == sym_a
        mask_b = positions_df["normalized_symbol"] == sym_b
        if mask_a.any():
            weight_a = positions_df.loc[mask_a, "weight_pct"].sum()
        if mask_b.any():
            weight_b = positions_df.loc[mask_b, "weight_pct"].sum()

    combined_weight = round(weight_a + weight_b, 1)

    return (
        f"{sym_a} and {sym_b} are {strength} {direction} correlated "
        f"(r={correlation:.2f}). Combined they represent {combined_weight}% "
        f"of your portfolio. These holdings may not provide the diversification "
        f"benefit you expect."
    )
