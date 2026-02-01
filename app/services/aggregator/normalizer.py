"""Data normalization: clean SnapTrade positions into standardized DataFrames.

Handles ticker normalization (e.g., VGRO -> VGRO.TO for TSX),
currency standardization, and cost basis calculation.
"""

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.position import Position
from app.models.account import Account

logger = structlog.get_logger()

# Known Canadian ETF providers and their TSX-listed funds
_CANADIAN_EXCHANGES = {"TSX", "TSE", "CVE", "NEO", "XTSE", "XCNQ"}

# Common Wealthsimple ETFs that should map to .TO suffix for yfinance
_KNOWN_TSX_TICKERS = {
    "VGRO", "VBAL", "VEQT", "VBAL", "XGRO", "XEQT", "XBAL",
    "VFV", "XIC", "XUS", "VCN", "VAB", "ZAG", "ZSP", "VUN",
    "XIU", "XEF", "XEC", "ZEB", "ZWB", "HXT", "HXS", "BTCC",
}


def normalize_ticker(symbol: str, exchange: str | None) -> str:
    """Normalize a ticker for yfinance compatibility.

    SnapTrade provides exchange info — use it to determine the correct suffix.
    - TSX/TSE listed -> append .TO
    - NEO listed -> append .NE
    - US exchanges (NYSE, NASDAQ) -> no suffix
    """
    if not symbol:
        return symbol

    # Already has a suffix
    if "." in symbol:
        return symbol

    # Exchange-based normalization
    if exchange and exchange.upper() in _CANADIAN_EXCHANGES:
        return f"{symbol}.TO"

    # Known Canadian tickers without exchange info
    if symbol.upper() in _KNOWN_TSX_TICKERS:
        return f"{symbol}.TO"

    return symbol


async def build_positions_dataframe(
    db: AsyncSession, user_id: str
) -> pd.DataFrame:
    """Build a standardized DataFrame of all user positions.

    Columns: symbol, normalized_symbol, description, asset_class, units,
             cost_basis_cents, market_value_cents, currency, exchange,
             last_price_cents, account_name, account_type,
             gain_loss_cents, gain_loss_pct, weight_pct
    """
    stmt = (
        select(Position, Account)
        .join(Account, Position.account_id == Account.id)
        .where(Position.user_id == user_id)
    )
    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return pd.DataFrame()

    records = []
    for position, account in rows:
        gain_loss = position.market_value_cents - position.cost_basis_cents
        gain_loss_pct = (
            (gain_loss / position.cost_basis_cents * 100)
            if position.cost_basis_cents != 0
            else 0.0
        )

        records.append({
            "symbol": position.symbol,
            "normalized_symbol": normalize_ticker(position.symbol, position.exchange),
            "description": position.description,
            "asset_class": position.asset_class.value if position.asset_class else "other",
            "units": float(position.units),
            "cost_basis_cents": position.cost_basis_cents,
            "market_value_cents": position.market_value_cents,
            "currency": position.currency.value if position.currency else "CAD",
            "exchange": position.exchange,
            "last_price_cents": position.last_price_cents,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "gain_loss_cents": gain_loss,
            "gain_loss_pct": round(gain_loss_pct, 2),
        })

    df = pd.DataFrame(records)

    # Calculate portfolio weight
    total_value = df["market_value_cents"].sum()
    if total_value > 0:
        df["weight_pct"] = round(df["market_value_cents"] / total_value * 100, 2)
    else:
        df["weight_pct"] = 0.0

    logger.info(
        "positions_dataframe_built",
        user_id=user_id,
        positions=len(df),
        total_value_cents=int(total_value),
    )

    return df
