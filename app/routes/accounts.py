"""Account listing endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account

router = APIRouter()


@router.get("/{user_id}")
async def list_accounts(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """List all accounts for a user."""
    stmt = select(Account).where(Account.user_id == user_id)
    result = await db.execute(stmt)
    accounts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "account_name": a.account_name,
            "account_type": a.account_type,
            "currency": a.currency.value if a.currency else "CAD",
            "connection_id": str(a.connection_id),
        }
        for a in accounts
    ]
