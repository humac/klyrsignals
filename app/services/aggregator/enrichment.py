"""Historical data enrichment using yfinance.

Fetches: 36-month price history, sector/geographic weightings for ETF look-through.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd
import numpy as np
import yfinance as yf
import structlog
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory
from app.models.sector_weight import SectorWeight

logger = structlog.get_logger()

# ETF look-through: known sector/country breakdowns for popular Canadian ETFs
# This serves as a fallback when yfinance can't provide fund details
_ETF_LOOKTHROUGH = {
    "VGRO.TO": {
        "sectors": {
            "Financials": 18.5, "Technology": 14.2, "Industrials": 10.1,
            "Healthcare": 8.5, "Consumer Discretionary": 7.8,
            "Energy": 5.2, "Materials": 4.1, "Utilities": 3.0,
            "Real Estate": 3.5, "Communication Services": 5.1,
            "Fixed Income": 20.0,
        },
        "countries": {
            "USA": 42.0, "CAN": 24.0, "JPN": 4.5, "GBR": 3.2,
            "CHN": 2.8, "DEU": 2.0, "FRA": 1.8, "AUS": 1.5,
            "OTHER": 18.2,
        },
    },
    "VEQT.TO": {
        "sectors": {
            "Financials": 19.5, "Technology": 18.0, "Industrials": 11.5,
            "Healthcare": 10.5, "Consumer Discretionary": 9.5,
            "Energy": 6.0, "Materials": 5.0, "Utilities": 3.5,
            "Real Estate": 3.5, "Communication Services": 6.0,
            "Consumer Staples": 7.0,
        },
        "countries": {
            "USA": 44.0, "CAN": 30.0, "JPN": 5.5, "GBR": 3.8,
            "CHN": 3.5, "DEU": 2.2, "FRA": 2.0, "AUS": 1.8,
            "OTHER": 7.2,
        },
    },
    "XGRO.TO": {
        "sectors": {
            "Financials": 18.0, "Technology": 14.5, "Industrials": 10.0,
            "Healthcare": 8.8, "Consumer Discretionary": 7.5,
            "Energy": 5.5, "Materials": 4.0, "Utilities": 3.2,
            "Real Estate": 3.0, "Communication Services": 5.5,
            "Fixed Income": 20.0,
        },
        "countries": {
            "USA": 41.0, "CAN": 25.0, "JPN": 4.2, "GBR": 3.0,
            "CHN": 2.5, "DEU": 2.0, "FRA": 1.8, "AUS": 1.5,
            "OTHER": 19.0,
        },
    },
    "XEQT.TO": {
        "sectors": {
            "Financials": 20.0, "Technology": 18.5, "Industrials": 11.0,
            "Healthcare": 10.0, "Consumer Discretionary": 9.0,
            "Energy": 6.5, "Materials": 5.0, "Utilities": 3.5,
            "Real Estate": 3.5, "Communication Services": 6.0,
            "Consumer Staples": 7.0,
        },
        "countries": {
            "USA": 45.0, "CAN": 25.0, "JPN": 5.0, "GBR": 3.5,
            "CHN": 3.0, "DEU": 2.5, "FRA": 2.0, "AUS": 1.8,
            "OTHER": 12.2,
        },
    },
    "VFV.TO": {
        "sectors": {
            "Technology": 29.0, "Healthcare": 13.0, "Financials": 13.0,
            "Consumer Discretionary": 10.5, "Communication Services": 9.0,
            "Industrials": 8.5, "Consumer Staples": 6.0, "Energy": 4.0,
            "Utilities": 2.5, "Real Estate": 2.5, "Materials": 2.0,
        },
        "countries": {"USA": 100.0},
    },
    "XIC.TO": {
        "sectors": {
            "Financials": 35.0, "Energy": 16.0, "Materials": 11.0,
            "Industrials": 11.0, "Technology": 8.0, "Utilities": 5.0,
            "Communication Services": 5.0, "Consumer Discretionary": 4.0,
            "Consumer Staples": 3.0, "Healthcare": 1.0, "Real Estate": 1.0,
        },
        "countries": {"CAN": 100.0},
    },
}

# Known Canadian banks/financials for home bias detection
_CANADIAN_FINANCIALS = {
    "BNS.TO", "BNS", "TD.TO", "TD", "RY.TO", "RY", "BMO.TO", "BMO",
    "CM.TO", "CM", "NA.TO", "NA", "MFC.TO", "MFC", "SLF.TO", "SLF",
    "GWO.TO", "IAG.TO", "POW.TO", "FFH.TO",
}


async def fetch_price_history(
    db: AsyncSession,
    symbols: list[str],
    period: str = "3y",
) -> dict[str, pd.DataFrame]:
    """Fetch trailing price history for a list of tickers using yfinance.

    Returns a dict of {symbol: DataFrame with columns [date, close_cents, volume]}.
    Also persists to the price_history table.
    """
    results = {}

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                logger.warning("yfinance_no_data", symbol=symbol)
                continue

            df = pd.DataFrame({
                "date": hist.index.tz_localize(None) if hist.index.tz else hist.index,
                "close": hist["Close"].values,
                "volume": hist["Volume"].values.astype(np.int64),
            })
            df["close_cents"] = (df["close"] * 100).round().astype(np.int64)
            df["symbol"] = symbol

            results[symbol] = df

            # Persist to database
            await _persist_price_history(db, symbol, df)

            logger.info("yfinance_fetched", symbol=symbol, rows=len(df))

        except Exception as e:
            logger.error("yfinance_fetch_failed", symbol=symbol, error=str(e))

    return results


async def fetch_sector_weights(
    db: AsyncSession,
    symbols: list[str],
) -> dict[str, dict]:
    """Fetch sector and geographic weights for each symbol.

    Uses yfinance fund data for ETFs, falls back to static look-through data,
    and uses individual stock sector for single equities.
    """
    results = {}

    for symbol in symbols:
        try:
            weights = {"sectors": {}, "countries": {}}

            # Check static look-through first (more reliable for Canadian ETFs)
            if symbol in _ETF_LOOKTHROUGH:
                weights = _ETF_LOOKTHROUGH[symbol]
            else:
                ticker = yf.Ticker(symbol)
                info = ticker.info or {}

                # For individual stocks
                sector = info.get("sector")
                country = info.get("country", "Unknown")
                country_code = _country_to_code(country)

                if sector:
                    weights["sectors"] = {sector: 100.0}
                    weights["countries"] = {country_code: 100.0}
                else:
                    # Try to get fund sector weights
                    try:
                        fund_sectors = ticker.funds_data.sector_weightings if hasattr(ticker, 'funds_data') else {}
                        if fund_sectors:
                            weights["sectors"] = {
                                k: round(v * 100, 2) for k, v in fund_sectors.items()
                            }
                    except Exception:
                        pass

            results[symbol] = weights

            # Persist sector weights
            await _persist_sector_weights(db, symbol, weights)

            logger.info("sector_weights_fetched", symbol=symbol)

        except Exception as e:
            logger.error("sector_weights_failed", symbol=symbol, error=str(e))

    return results


async def _persist_price_history(
    db: AsyncSession,
    symbol: str,
    df: pd.DataFrame,
) -> None:
    """Upsert price history rows into the database."""
    # Delete existing data for this symbol to avoid conflicts
    await db.execute(
        delete(PriceHistory).where(PriceHistory.symbol == symbol)
    )

    for _, row in df.iterrows():
        price = PriceHistory(
            time=row["date"].to_pydatetime().replace(tzinfo=timezone.utc),
            symbol=symbol,
            close_cents=int(row["close_cents"]),
            volume=int(row["volume"]),
        )
        db.add(price)

    await db.flush()


async def _persist_sector_weights(
    db: AsyncSession,
    symbol: str,
    weights: dict,
) -> None:
    """Persist sector/country weights to the cache table."""
    # Clear old data
    await db.execute(
        delete(SectorWeight).where(SectorWeight.symbol == symbol)
    )

    now = datetime.now(timezone.utc)

    for sector, pct in weights.get("sectors", {}).items():
        for country, country_pct in weights.get("countries", {}).items():
            sw = SectorWeight(
                symbol=symbol,
                sector=sector,
                country=country,
                weight_pct=round(float(pct) * float(country_pct) / 100, 2),
                source="yfinance",
                fetched_at=now,
            )
            db.add(sw)

    await db.flush()


def _country_to_code(country_name: str) -> str:
    """Convert full country name to 3-letter ISO code."""
    mapping = {
        "United States": "USA", "Canada": "CAN", "Japan": "JPN",
        "United Kingdom": "GBR", "China": "CHN", "Germany": "DEU",
        "France": "FRA", "Australia": "AUS", "Switzerland": "CHE",
        "South Korea": "KOR", "Netherlands": "NLD", "Sweden": "SWE",
        "Hong Kong": "HKG", "India": "IND", "Brazil": "BRA",
        "Taiwan": "TWN", "Singapore": "SGP", "Ireland": "IRL",
    }
    return mapping.get(country_name, "OTH")
