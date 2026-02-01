"""Position and portfolio endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.position import Position
from app.models.account import Account
from app.schemas.position import PositionResponse, AccountSummary, PortfolioSummary

router = APIRouter()


@router.get("/{user_id}", response_model=PortfolioSummary)
async def get_portfolio(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get full portfolio summary with all positions grouped by account."""
    # Fetch all positions with account info
    stmt = (
        select(Position, Account)
        .join(Account, Position.account_id == Account.id)
        .where(Position.user_id == user_id)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Group by account
    accounts_map: dict[uuid.UUID, dict] = {}
    for position, account in rows:
        acct_id = account.id
        if acct_id not in accounts_map:
            accounts_map[acct_id] = {
                "account": account,
                "positions": [],
                "total_market_value_cents": 0,
                "total_cost_basis_cents": 0,
            }
        accounts_map[acct_id]["positions"].append(position)
        accounts_map[acct_id]["total_market_value_cents"] += position.market_value_cents
        accounts_map[acct_id]["total_cost_basis_cents"] += position.cost_basis_cents

    # Build response
    account_summaries = []
    total_market = 0
    total_cost = 0

    for acct_id, data in accounts_map.items():
        acct = data["account"]
        mv = data["total_market_value_cents"]
        cb = data["total_cost_basis_cents"]
        gl = mv - cb
        gl_pct = (gl / cb * 100) if cb != 0 else 0.0

        total_market += mv
        total_cost += cb

        position_responses = [
            PositionResponse.model_validate(p) for p in data["positions"]
        ]

        account_summaries.append(AccountSummary(
            account_id=acct_id,
            account_name=acct.account_name,
            account_type=acct.account_type,
            currency=acct.currency.value if acct.currency else "CAD",
            total_market_value_cents=mv,
            total_cost_basis_cents=cb,
            gain_loss_cents=gl,
            gain_loss_pct=round(gl_pct, 2),
            positions=position_responses,
        ))

    total_gl = total_market - total_cost
    total_gl_pct = (total_gl / total_cost * 100) if total_cost != 0 else 0.0

    return PortfolioSummary(
        user_id=user_id,
        total_market_value_cents=total_market,
        total_cost_basis_cents=total_cost,
        total_gain_loss_cents=total_gl,
        total_gain_loss_pct=round(total_gl_pct, 2),
        accounts=account_summaries,
    ).model_dump()
