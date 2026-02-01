"""SnapTrade integration service for Wealthsimple and other brokerages.

Handles: user registration, connection portal, account/holdings sync.
"""

import uuid
from datetime import datetime, timezone

import structlog
from snaptrade_client import SnapTrade
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import SnapTradeError, UserNotFoundError
from app.models.user import User
from app.models.connection import Connection, ConnectionStatus
from app.models.account import Account, Currency
from app.models.position import Position, AssetClass
from app.security import encrypt_token, decrypt_token

logger = structlog.get_logger()


def _get_client() -> SnapTrade:
    """Create a SnapTrade SDK client."""
    return SnapTrade(
        consumer_key=settings.snaptrade_consumer_key,
        client_id=settings.snaptrade_client_id,
    )


def _to_cents(value: float | int | None) -> int:
    """Convert a dollar float to cents integer."""
    if value is None:
        return 0
    return int(round(float(value) * 100))


def _classify_asset(security_type: str | None) -> AssetClass:
    """Map SnapTrade security type to our asset class enum."""
    if not security_type:
        return AssetClass.EQUITY
    st = security_type.lower()
    if st in ("equity", "stock", "etf", "mutual_fund"):
        return AssetClass.EQUITY
    if st in ("bond", "fixed_income", "fixed income"):
        return AssetClass.FIXED_INCOME
    if st in ("cash", "money_market", "currency"):
        return AssetClass.CASH
    if st in ("crypto", "cryptocurrency"):
        return AssetClass.CRYPTO
    return AssetClass.OTHER


async def register_user(db: AsyncSession, user: User) -> User:
    """Register a user with SnapTrade and store encrypted credentials.

    SnapTrade requires each user to be registered with a unique user_id
    before they can connect brokerages.
    """
    client = _get_client()
    try:
        response = client.authentication.register_snap_trade_user(
            user_id=str(user.id),
        )
        user.snaptrade_user_id = response.user_id
        user.snaptrade_user_secret = encrypt_token(response.user_secret)
        await db.flush()
        logger.info("snaptrade_user_registered", user_id=str(user.id))
        return user
    except Exception as e:
        logger.error("snaptrade_registration_failed", error=str(e))
        raise SnapTradeError(f"Failed to register user with SnapTrade: {e}")


async def get_connection_portal_url(
    db: AsyncSession, user: User, brokerage_name: str = "Wealthsimple"
) -> tuple[str, uuid.UUID]:
    """Generate a SnapTrade connection portal URL for the user.

    Returns (redirect_url, connection_id) tuple.
    The user should be redirected to this URL to authenticate with their brokerage.
    """
    if not user.snaptrade_user_id or not user.snaptrade_user_secret:
        user = await register_user(db, user)

    user_secret = decrypt_token(user.snaptrade_user_secret)
    client = _get_client()

    try:
        response = client.authentication.login_snap_trade_user(
            user_id=user.snaptrade_user_id,
            user_secret=user_secret,
        )
        redirect_url = response.redirect_uri

        # Create a connection record to track this
        connection = Connection(
            user_id=user.id,
            brokerage_name=brokerage_name,
            status=ConnectionStatus.ACTIVE,
        )
        db.add(connection)
        await db.flush()

        logger.info("snaptrade_portal_generated", user_id=str(user.id))
        return redirect_url, connection.id

    except Exception as e:
        logger.error("snaptrade_portal_failed", error=str(e))
        raise SnapTradeError(f"Failed to generate connection portal: {e}")


async def sync_accounts(db: AsyncSession, user: User) -> list[Account]:
    """Fetch all accounts from SnapTrade for this user and upsert them."""
    if not user.snaptrade_user_id or not user.snaptrade_user_secret:
        raise SnapTradeError("User not registered with SnapTrade")

    user_secret = decrypt_token(user.snaptrade_user_secret)
    client = _get_client()

    try:
        accounts_response = client.account_information.list_user_accounts(
            user_id=user.snaptrade_user_id,
            user_secret=user_secret,
        )

        synced_accounts = []
        for acct_data in accounts_response:
            # Find or create the connection
            connection = await _get_or_create_connection(
                db, user, acct_data
            )

            # Upsert account
            stmt = select(Account).where(
                Account.snaptrade_account_id == str(acct_data.id)
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()

            if account is None:
                account = Account(
                    connection_id=connection.id,
                    user_id=user.id,
                    snaptrade_account_id=str(acct_data.id),
                    account_name=acct_data.name or "Unknown",
                    account_type=getattr(acct_data, "type", None),
                    currency=Currency.CAD if getattr(acct_data, "currency", "CAD") == "CAD" else Currency.USD,
                )
                db.add(account)
            else:
                account.account_name = acct_data.name or account.account_name

            await db.flush()
            synced_accounts.append(account)

        logger.info(
            "snaptrade_accounts_synced",
            user_id=str(user.id),
            count=len(synced_accounts),
        )
        return synced_accounts

    except SnapTradeError:
        raise
    except Exception as e:
        logger.error("snaptrade_accounts_sync_failed", error=str(e))
        raise SnapTradeError(f"Failed to sync accounts: {e}")


async def sync_positions(db: AsyncSession, user: User) -> list[Position]:
    """Fetch all holdings from all accounts and upsert positions."""
    if not user.snaptrade_user_id or not user.snaptrade_user_secret:
        raise SnapTradeError("User not registered with SnapTrade")

    user_secret = decrypt_token(user.snaptrade_user_secret)
    client = _get_client()

    try:
        holdings_response = client.account_information.get_all_user_holdings(
            user_id=user.snaptrade_user_id,
            user_secret=user_secret,
        )

        all_positions = []

        for account_holding in holdings_response:
            snaptrade_account_id = str(account_holding.account.id)

            # Find our local account
            stmt = select(Account).where(
                Account.snaptrade_account_id == snaptrade_account_id,
                Account.user_id == user.id,
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            if account is None:
                continue

            # Clear existing positions for this account before re-syncing
            old_positions_stmt = select(Position).where(
                Position.account_id == account.id
            )
            old_result = await db.execute(old_positions_stmt)
            for old_pos in old_result.scalars().all():
                await db.delete(old_pos)

            # Process each position
            for pos_data in (account_holding.positions or []):
                symbol_obj = getattr(pos_data, "symbol", None)

                symbol = _extract_symbol(symbol_obj, pos_data)
                if not symbol:
                    continue

                exchange = None
                description = None
                if symbol_obj:
                    exchange = getattr(symbol_obj, "exchange", None)
                    if exchange and hasattr(exchange, "code"):
                        exchange = exchange.code
                    description = getattr(symbol_obj, "description", None)

                currency = Currency.CAD
                if symbol_obj and hasattr(symbol_obj, "currency"):
                    curr = getattr(symbol_obj.currency, "code", "CAD") if symbol_obj.currency else "CAD"
                    currency = Currency.USD if curr == "USD" else Currency.CAD

                units = float(getattr(pos_data, "units", 0) or 0)
                price = float(getattr(pos_data, "price", 0) or 0)
                avg_cost = float(getattr(pos_data, "average_purchase_price", 0) or 0)

                position = Position(
                    account_id=account.id,
                    user_id=user.id,
                    symbol=symbol,
                    description=description,
                    asset_class=_classify_asset(
                        getattr(symbol_obj, "type", None) if symbol_obj else None
                    ),
                    units=units,
                    cost_basis_cents=_to_cents(avg_cost * units),
                    market_value_cents=_to_cents(price * units),
                    currency=currency,
                    exchange=str(exchange) if exchange else None,
                    last_price_cents=_to_cents(price),
                )
                db.add(position)
                all_positions.append(position)

            await db.flush()

        # Update connection sync timestamps
        stmt = select(Connection).where(Connection.user_id == user.id)
        result = await db.execute(stmt)
        for conn in result.scalars().all():
            conn.last_synced_at = datetime.now(timezone.utc)

        logger.info(
            "snaptrade_positions_synced",
            user_id=str(user.id),
            count=len(all_positions),
        )
        return all_positions

    except SnapTradeError:
        raise
    except Exception as e:
        logger.error("snaptrade_positions_sync_failed", error=str(e))
        raise SnapTradeError(f"Failed to sync positions: {e}")


def _extract_symbol(symbol_obj: object | None, pos_data: object) -> str | None:
    """Extract the ticker symbol from various SnapTrade response shapes."""
    if symbol_obj:
        # Try symbol.symbol first (most common)
        sym = getattr(symbol_obj, "symbol", None)
        if sym:
            raw = getattr(sym, "symbol", None) if hasattr(sym, "symbol") else str(sym)
            if raw:
                return raw

    # Fallback to pos_data.symbol as string
    raw = getattr(pos_data, "symbol", None)
    if isinstance(raw, str):
        return raw

    return None


async def _get_or_create_connection(
    db: AsyncSession, user: User, acct_data: object
) -> Connection:
    """Find existing connection or create one for this brokerage."""
    brokerage_name = "Unknown"
    meta = getattr(acct_data, "meta", None)
    if meta:
        brokerage_name = getattr(meta, "brokerage_name", "Unknown") or "Unknown"
    elif hasattr(acct_data, "institution_name"):
        brokerage_name = acct_data.institution_name or "Unknown"

    stmt = select(Connection).where(
        Connection.user_id == user.id,
        Connection.brokerage_name == brokerage_name,
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if connection is None:
        connection = Connection(
            user_id=user.id,
            brokerage_name=brokerage_name,
            status=ConnectionStatus.ACTIVE,
        )
        db.add(connection)
        await db.flush()

    return connection
