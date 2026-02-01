"""AnalystService: orchestrates the full analysis pipeline.

Coordinates: data normalization -> enrichment -> concentration audit ->
correlation analysis -> AI signal generation.
"""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_result import AnalysisResult
from app.schemas.analysis import (
    FullAnalysisResponse,
    ConcentrationReport,
    CorrelationReport,
    KlyrSignal,
)
from app.services.aggregator.normalizer import build_positions_dataframe
from app.services.aggregator.enrichment import fetch_price_history, fetch_sector_weights
from app.services.auditor.concentration import run_concentration_audit
from app.services.auditor.correlation import run_correlation_analysis
from app.services.ai.context_generator import build_analysis_prompt
from app.services.ai.llm_connector import generate_signals

logger = structlog.get_logger()


async def run_full_analysis(
    db: AsyncSession,
    user_id: uuid.UUID,
    skip_enrichment: bool = False,
) -> FullAnalysisResponse:
    """Run the complete KlyrSignals analysis pipeline.

    Steps:
    1. Build normalized positions DataFrame
    2. Fetch historical price data (yfinance)
    3. Fetch sector/geographic weights (look-through)
    4. Run concentration audit
    5. Run correlation analysis
    6. Generate AI signals
    7. Persist results

    Args:
        db: Database session
        user_id: User to analyze
        skip_enrichment: Skip yfinance calls (use cached data only)
    """
    logger.info("analysis_pipeline_started", user_id=str(user_id))

    # Step 1: Build positions DataFrame
    positions_df = await build_positions_dataframe(db, str(user_id))

    if positions_df.empty:
        return FullAnalysisResponse(
            user_id=user_id,
            concentration=ConcentrationReport(
                alerts=[], sector_weights={}, country_weights={}, home_bias_pct=0.0
            ),
            correlation=CorrelationReport(hidden_twins=[], correlation_matrix={}),
            signals=[],
            ai_summary="No positions found. Please sync your brokerage account first.",
            analyzed_at=datetime.now(timezone.utc),
        )

    # Step 2 & 3: Enrichment (parallel-friendly in concept, sequential here)
    symbols = positions_df["normalized_symbol"].unique().tolist()

    price_histories = {}
    sector_weights = {}

    if not skip_enrichment:
        price_histories = await fetch_price_history(db, symbols)
        sector_weights = await fetch_sector_weights(db, symbols)
    else:
        logger.info("enrichment_skipped", reason="skip_enrichment flag")

    # Step 4: Concentration audit
    concentration = run_concentration_audit(positions_df, sector_weights)

    # Step 5: Correlation analysis
    correlation = run_correlation_analysis(price_histories, positions_df)

    # Step 6: Generate AI signals
    system_prompt, user_prompt = build_analysis_prompt(
        positions_df, concentration, correlation
    )

    ai_signals, ai_summary = await generate_signals(system_prompt, user_prompt)

    # Merge rule-based alerts into signals if AI didn't cover them
    all_signals = _merge_signals(ai_signals, concentration, correlation)

    # Step 7: Persist results
    result = AnalysisResult(
        user_id=user_id,
        analysis_type="full_analysis",
        result_json={
            "concentration": concentration.model_dump(),
            "correlation": correlation.model_dump(),
            "signals": [s.model_dump() for s in all_signals],
        },
        ai_summary=ai_summary,
    )
    db.add(result)
    await db.flush()

    logger.info(
        "analysis_pipeline_complete",
        user_id=str(user_id),
        signals=len(all_signals),
        alerts=len(concentration.alerts),
    )

    return FullAnalysisResponse(
        user_id=user_id,
        concentration=concentration,
        correlation=correlation,
        signals=all_signals,
        ai_summary=ai_summary if ai_summary else "Analysis complete.",
        analyzed_at=datetime.now(timezone.utc),
    )


def _merge_signals(
    ai_signals: list[KlyrSignal],
    concentration: ConcentrationReport,
    correlation: CorrelationReport,
) -> list[KlyrSignal]:
    """Merge AI-generated signals with rule-based fallback signals.

    If the AI is unavailable or misses key findings, ensure critical
    concentration and correlation alerts are still represented as signals.
    """
    signals = list(ai_signals)
    ai_categories = {(s.category, s.title) for s in ai_signals}

    # Add rule-based concentration signals
    sig_counter = len(signals) + 1

    for alert in concentration.alerts:
        # Check if AI already covered this
        if any(alert.name.lower() in s.title.lower() for s in ai_signals):
            continue

        if alert.category == "home_bias":
            signals.append(KlyrSignal(
                signal_id=f"SIG-AUTO-{sig_counter:03d}",
                title=f"Canadian Home Bias: {alert.weight_pct:.0f}%",
                description=(
                    f"Your portfolio has {alert.weight_pct:.1f}% exposure to Canadian assets, "
                    f"exceeding the {alert.threshold_pct:.0f}% threshold. "
                    f"Canada represents only ~3% of global market capitalization. "
                    f"Over-concentration in your home market increases vulnerability to "
                    f"domestic economic shocks."
                ),
                severity=alert.severity,
                category="home_bias",
                affected_holdings=[],
                recommendation=(
                    "Consider increasing international diversification through "
                    "global equity ETFs (e.g., XAW, VXC) to reduce home bias."
                ),
            ))
        elif alert.category == "sector":
            signals.append(KlyrSignal(
                signal_id=f"SIG-AUTO-{sig_counter:03d}",
                title=f"{alert.name} Sector Concentration: {alert.weight_pct:.0f}%",
                description=(
                    f"Your look-through {alert.name} sector exposure is {alert.weight_pct:.1f}%, "
                    f"exceeding the {alert.threshold_pct:.0f}% threshold. "
                    f"A sector-specific downturn could have an outsized impact on your portfolio."
                ),
                severity=alert.severity,
                category="concentration",
                affected_holdings=[],
                recommendation=f"Review holdings with {alert.name} exposure and consider rebalancing.",
            ))

        sig_counter += 1

    # Add rule-based correlation signals
    for twin in correlation.hidden_twins:
        if any(twin.symbol_a in s.affected_holdings and twin.symbol_b in s.affected_holdings for s in ai_signals):
            continue

        signals.append(KlyrSignal(
            signal_id=f"SIG-AUTO-{sig_counter:03d}",
            title=f"Hidden Twin: {twin.symbol_a} & {twin.symbol_b}",
            description=twin.explanation,
            severity="warning",
            category="correlation",
            affected_holdings=[twin.symbol_a, twin.symbol_b],
            recommendation=(
                f"Review whether holding both {twin.symbol_a} and {twin.symbol_b} "
                f"provides meaningful diversification given their {twin.correlation:.0%} correlation."
            ),
        ))
        sig_counter += 1

    return signals
