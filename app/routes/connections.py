"""Brokerage connection endpoints (SnapTrade OAuth flow)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.connection import Connection
from app.schemas.connection import ConnectionCreate, ConnectionResponse, SnapTradeRedirectResponse
from app.services.aggregator.snaptrade_service import (
    get_connection_portal_url,
    sync_accounts,
    sync_positions,
)
from app.exceptions import SnapTradeError

router = APIRouter()


@router.post("/connect", response_model=SnapTradeRedirectResponse)
async def start_connection(
    payload: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start a SnapTrade connection flow.

    Returns a redirect URL where the user authenticates with their brokerage.
    """
    stmt = select(User).where(User.id == payload.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        redirect_url, connection_id = await get_connection_portal_url(
            db, user, payload.brokerage_name
        )
        return {"redirect_url": redirect_url, "connection_id": connection_id}
    except SnapTradeError as e:
        raise HTTPException(status_code=502, detail=str(e.message))


@router.post("/{user_id}/sync")
async def sync_user_data(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Sync all accounts and positions from SnapTrade for a user.

    Call this after the user completes the connection portal flow.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        accounts = await sync_accounts(db, user)
        positions = await sync_positions(db, user)
        return {
            "accounts_synced": len(accounts),
            "positions_synced": len(positions),
            "status": "success",
        }
    except SnapTradeError as e:
        raise HTTPException(status_code=502, detail=str(e.message))


@router.get("/{user_id}", response_model=list[ConnectionResponse])
async def list_connections(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Connection]:
    """List all brokerage connections for a user."""
    stmt = select(Connection).where(Connection.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
