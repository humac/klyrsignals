"""AI Context Generator: transforms portfolio data into high-density LLM prompts.

Builds structured context from positions DataFrame, concentration report,
and correlation report for the AI to generate strategic signals.
"""

import pandas as pd
import structlog

from app.schemas.analysis import ConcentrationReport, CorrelationReport
from app.security import strip_pii

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are KlyrSignals, an expert financial portfolio analyst specializing in
Canadian investment portfolios. You analyze holdings data to identify blind spots,
concentration risks, and actionable insights.

Your analysis must be:
1. Specific — reference actual holdings and percentages
2. Actionable — provide concrete recommendations
3. Risk-aware — flag interest rate sensitivity, currency risk, and sector concentration
4. Canadian-context-aware — understand TFSA, RRSP, RESP implications and Canadian home bias

Output your response as a JSON array of signals, each with:
- signal_id: unique string (e.g., "SIG-001")
- title: short title (< 80 chars)
- description: detailed explanation (2-4 sentences)
- severity: "info" | "warning" | "critical"
- category: "concentration" | "correlation" | "home_bias" | "interest_rate" | "currency" | "opportunity"
- affected_holdings: list of ticker symbols involved
- recommendation: specific action to consider (1-2 sentences)

Respond ONLY with the JSON array. No markdown, no code fences."""


def build_analysis_prompt(
    positions_df: pd.DataFrame,
    concentration: ConcentrationReport,
    correlation: CorrelationReport,
) -> tuple[str, str]:
    """Build the system prompt and user context for AI analysis.

    Returns (system_prompt, user_prompt) tuple.
    The user_prompt contains all sanitized portfolio data.
    """
    # Build portfolio summary section
    total_value = positions_df["market_value_cents"].sum() if not positions_df.empty else 0
    total_cost = positions_df["cost_basis_cents"].sum() if not positions_df.empty else 0
    total_gain = total_value - total_cost
    gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

    holdings_text = _format_holdings(positions_df)
    concentration_text = _format_concentration(concentration)
    correlation_text = _format_correlation(correlation)

    user_prompt = f"""PORTFOLIO ANALYSIS REQUEST
========================

PORTFOLIO SUMMARY
Total Market Value: ${total_value / 100:,.2f}
Total Cost Basis: ${total_cost / 100:,.2f}
Total Gain/Loss: ${total_gain / 100:,.2f} ({gain_pct:+.1f}%)
Number of Holdings: {len(positions_df) if not positions_df.empty else 0}

CURRENT HOLDINGS
{holdings_text}

CONCENTRATION ANALYSIS
{concentration_text}

CORRELATION ANALYSIS
{correlation_text}

Please analyze this portfolio and generate strategic signals identifying blind spots,
concentration risks, diversification gaps, and opportunities for improvement.
Focus especially on:
1. Canadian home bias risks
2. Hidden correlations between holdings
3. Sector/geographic concentration vulnerabilities
4. Interest rate sensitivity (if applicable)
5. Currency risk exposure"""

    return SYSTEM_PROMPT, user_prompt


def _format_holdings(df: pd.DataFrame) -> str:
    """Format holdings into a readable table for the AI."""
    if df.empty:
        return "No holdings data available."

    lines = []
    lines.append(f"{'Symbol':<12} {'Type':<12} {'Value':>12} {'Weight':>8} {'Gain%':>8} {'Account':<15}")
    lines.append("-" * 70)

    for _, row in df.iterrows():
        value = f"${row['market_value_cents'] / 100:,.2f}"
        lines.append(
            f"{row['symbol']:<12} "
            f"{row['asset_class']:<12} "
            f"{value:>12} "
            f"{row['weight_pct']:>7.1f}% "
            f"{row['gain_loss_pct']:>+7.1f}% "
            f"{row.get('account_name', 'N/A'):<15}"
        )

    return "\n".join(lines)


def _format_concentration(report: ConcentrationReport) -> str:
    """Format concentration audit results."""
    lines = []

    lines.append(f"Home Bias (Canada): {report.home_bias_pct:.1f}%")
    lines.append("")

    lines.append("Sector Exposure (Look-Through):")
    for sector, pct in sorted(report.sector_weights.items(), key=lambda x: -x[1]):
        marker = " ⚠" if pct >= 25 else ""
        lines.append(f"  {sector}: {pct:.1f}%{marker}")

    lines.append("")
    lines.append("Geographic Exposure:")
    for country, pct in sorted(report.country_weights.items(), key=lambda x: -x[1]):
        lines.append(f"  {country}: {pct:.1f}%")

    if report.alerts:
        lines.append("")
        lines.append("ALERTS:")
        for alert in report.alerts:
            lines.append(
                f"  [{alert.severity.upper()}] {alert.category}: "
                f"{alert.name} at {alert.weight_pct:.1f}% "
                f"(threshold: {alert.threshold_pct:.1f}%)"
            )

    return "\n".join(lines)


def _format_correlation(report: CorrelationReport) -> str:
    """Format correlation analysis results."""
    lines = []

    if report.hidden_twins:
        lines.append("HIDDEN TWINS (Corr > 0.80):")
        for twin in report.hidden_twins:
            lines.append(
                f"  {twin.symbol_a} <-> {twin.symbol_b}: "
                f"r={twin.correlation:.2f}"
            )
            lines.append(f"    {twin.explanation}")
    else:
        lines.append("No hidden twins detected (all pairwise correlations < 0.80)")

    if report.correlation_matrix:
        lines.append("")
        lines.append(f"Correlation matrix computed for {len(report.correlation_matrix)} symbols")

    return "\n".join(lines)
