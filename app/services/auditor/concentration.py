"""Concentration Auditor: detect sector, country, and home bias risks.

Thresholds (configurable):
- Any single sector > 25% = warning
- Any single sector > 40% = critical
- Canadian 'Home Bias' > 60% = warning
- Any single holding > 20% = warning
"""

import pandas as pd
import structlog

from app.schemas.analysis import ConcentrationAlert, ConcentrationReport
from app.services.aggregator.enrichment import _ETF_LOOKTHROUGH, _CANADIAN_FINANCIALS

logger = structlog.get_logger()

# Default thresholds
SECTOR_WARNING_PCT = 25.0
SECTOR_CRITICAL_PCT = 40.0
COUNTRY_WARNING_PCT = 35.0
HOME_BIAS_WARNING_PCT = 60.0
SINGLE_HOLDING_WARNING_PCT = 20.0


def run_concentration_audit(
    positions_df: pd.DataFrame,
    sector_weights: dict[str, dict],
) -> ConcentrationReport:
    """Perform a full concentration audit on the portfolio.

    Uses look-through analysis for ETFs to determine true sector/country exposure.
    """
    if positions_df.empty:
        return ConcentrationReport(
            alerts=[], sector_weights={}, country_weights={}, home_bias_pct=0.0
        )

    total_value = positions_df["market_value_cents"].sum()
    if total_value == 0:
        return ConcentrationReport(
            alerts=[], sector_weights={}, country_weights={}, home_bias_pct=0.0
        )

    # Calculate weighted sector exposure (look-through)
    agg_sectors: dict[str, float] = {}
    agg_countries: dict[str, float] = {}

    for _, row in positions_df.iterrows():
        symbol = row["normalized_symbol"]
        holding_weight = row["market_value_cents"] / total_value * 100

        weights = sector_weights.get(symbol, {})
        sectors = weights.get("sectors", {})
        countries = weights.get("countries", {})

        if sectors:
            for sector, pct in sectors.items():
                contribution = holding_weight * pct / 100
                agg_sectors[sector] = agg_sectors.get(sector, 0) + contribution
        else:
            # Unknown — classify as "Other"
            agg_sectors["Other"] = agg_sectors.get("Other", 0) + holding_weight

        if countries:
            for country, pct in countries.items():
                contribution = holding_weight * pct / 100
                agg_countries[country] = agg_countries.get(country, 0) + contribution
        else:
            agg_countries["Other"] = agg_countries.get("Other", 0) + holding_weight

    # Round everything
    agg_sectors = {k: round(v, 2) for k, v in agg_sectors.items()}
    agg_countries = {k: round(v, 2) for k, v in agg_countries.items()}

    # Calculate Canadian home bias
    home_bias_pct = agg_countries.get("CAN", 0.0)

    # Generate alerts
    alerts = []

    # Sector concentration alerts
    for sector, pct in agg_sectors.items():
        if pct >= SECTOR_CRITICAL_PCT:
            alerts.append(ConcentrationAlert(
                category="sector",
                name=sector,
                weight_pct=pct,
                threshold_pct=SECTOR_CRITICAL_PCT,
                severity="critical",
            ))
        elif pct >= SECTOR_WARNING_PCT:
            alerts.append(ConcentrationAlert(
                category="sector",
                name=sector,
                weight_pct=pct,
                threshold_pct=SECTOR_WARNING_PCT,
                severity="warning",
            ))

    # Country concentration alerts
    for country, pct in agg_countries.items():
        if pct >= COUNTRY_WARNING_PCT:
            alerts.append(ConcentrationAlert(
                category="country",
                name=country,
                weight_pct=pct,
                threshold_pct=COUNTRY_WARNING_PCT,
                severity="warning",
            ))

    # Home bias alert
    if home_bias_pct >= HOME_BIAS_WARNING_PCT:
        alerts.append(ConcentrationAlert(
            category="home_bias",
            name="Canada",
            weight_pct=home_bias_pct,
            threshold_pct=HOME_BIAS_WARNING_PCT,
            severity="critical" if home_bias_pct >= 75.0 else "warning",
        ))

    # Single holding concentration
    for _, row in positions_df.iterrows():
        weight = row.get("weight_pct", 0)
        if weight >= SINGLE_HOLDING_WARNING_PCT:
            alerts.append(ConcentrationAlert(
                category="single_holding",
                name=row["symbol"],
                weight_pct=weight,
                threshold_pct=SINGLE_HOLDING_WARNING_PCT,
                severity="warning",
            ))

    logger.info(
        "concentration_audit_complete",
        alerts=len(alerts),
        home_bias=home_bias_pct,
    )

    return ConcentrationReport(
        alerts=alerts,
        sector_weights=agg_sectors,
        country_weights=agg_countries,
        home_bias_pct=home_bias_pct,
    )
