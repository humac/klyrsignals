"""Analysis endpoints: run blind-spot detection and retrieve results."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.analysis_result import AnalysisResult
from app.schemas.analysis import FullAnalysisResponse
from app.services.ai.analyst import run_full_analysis

router = APIRouter()


@router.post("/{user_id}/run", response_model=FullAnalysisResponse)
async def trigger_analysis(
    user_id: uuid.UUID,
    skip_enrichment: bool = Query(
        default=False,
        description="Skip yfinance enrichment (use cached data)",
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Run the full KlyrSignals analysis pipeline for a user.

    This triggers:
    1. Position normalization
    2. Historical data enrichment (yfinance)
    3. Concentration audit
    4. Correlation analysis
    5. AI signal generation
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    analysis = await run_full_analysis(db, user_id, skip_enrichment=skip_enrichment)
    return analysis.model_dump()


@router.get("/{user_id}/latest", response_model=FullAnalysisResponse | None)
async def get_latest_analysis(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict | None:
    """Get the most recent analysis result for a user."""
    stmt = (
        select(AnalysisResult)
        .where(
            AnalysisResult.user_id == user_id,
            AnalysisResult.analysis_type == "full_analysis",
        )
        .order_by(AnalysisResult.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        return None

    return analysis.result_json


@router.get("/{user_id}/history")
async def get_analysis_history(
    user_id: uuid.UUID,
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get analysis history for a user."""
    stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.user_id == user_id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "analysis_type": a.analysis_type,
            "ai_summary": a.ai_summary[:200] if a.ai_summary else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]
