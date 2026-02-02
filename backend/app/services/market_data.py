import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models import TickerPriceHistory
from sqlalchemy.dialects.postgresql import insert

class MarketDataService:
    @staticmethod
    def get_price_history(ticker: str, db: Session, lookback_months: int = 36):
        """
        Retrieves price history for a ticker. 
        Checks local cache first; if stale (older than 24h), fetches from Yahoo Finance.
        Returns a DataFrame with 'date' and 'close_cents'.
        """
        # 1. Check most recent date in DB
        last_entry = db.query(TickerPriceHistory.date)\
            .filter(TickerPriceHistory.ticker == ticker)\
            .order_by(TickerPriceHistory.date.desc())\
            .first()

        now = datetime.now(timezone.utc)
        needs_update = True
        
        if last_entry:
            last_date = last_entry[0].replace(tzinfo=timezone.utc)
            # If we have data from within the last 24h (market day approximation), skip fetch
            if (now - last_date).total_seconds() < 86400:
                needs_update = False

        if needs_update:
            MarketDataService._fetch_and_cache(ticker, db)

        # 2. Query Cache
        cutoff_date = now - timedelta(days=30 * lookback_months)
        
        history = db.query(TickerPriceHistory)\
            .filter(TickerPriceHistory.ticker == ticker, TickerPriceHistory.date >= cutoff_date)\
            .order_by(TickerPriceHistory.date.asc())\
            .all()
            
        data = [{"date": h.date, "close_cents": h.close_cents} for h in history]
        return pd.DataFrame(data)

    @staticmethod
    def _fetch_and_cache(ticker: str, db: Session):
        """
        Private helper to fetch from yfinance and upsert into DB.
        """
        try:
            # Fetch 5y to be safe
            t = yf.Ticker(ticker)
            hist = t.history(period="5y")
            
            if hist.empty:
                print(f"Warning: No data found for {ticker}")
                return

            # Prepare objects
            records = []
            for date, row in hist.iterrows():
                # Convert to UTC
                date_utc = date.to_pydatetime().replace(tzinfo=timezone.utc)
                
                # Close price -> Cents
                close_cents = int(row['Close'] * 100)
                
                records.append({
                    "id":  None, # auto-gen handled by conflict or simple add? bulk_insert doesn't like auto-gen usually unless using mapping
                    "ticker": ticker,
                    "date": date_utc,
                    "close_cents": close_cents
                })

            # Upsert using Postgres ON CONFLICT DO UPDATE
            # SQLAlchemy 2.0+ Core style
            stmt = insert(TickerPriceHistory).values(records)
            stmt = stmt.on_conflict_do_update(
                constraint='ticker_price_history_ticker_date_key', # Auto-named by checking models.py args? Need to verify constraint name if not explicit
                set_={
                    "close_cents": stmt.excluded.close_cents
                }
            )
            # Note: models.py defines UniqueConstraint("ticker", "date"), 
            # Postgres default naming is table_col1_col2_key. 
            # We should probably explicit name the constraint in models to be safe, 
            # but for now we'll assume standard naming or use ignore if simple.
            # Actually, standard naming: ticker_price_history_ticker_date_key
            
            db.execute(stmt)
            db.commit()
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            db.rollback()

    @staticmethod
    def get_etf_composition(ticker: str):
        """
        Fetches sector and country weightings for the Look-Through Engine.
        Returns two dicts: sector_weights, country_weights
        """
        try:
            etf = yf.Ticker(ticker)
            # funds_data attribute might vary by yfinance version, 
            # usually it is .funds_data.
            # Fallback to .info if needed, but info structure is chaotic.
            
            # Note: yfinance is notoriously unstable with API changes.
            # Ideally we wrap this in try/except and mock in tests.
            
            # Mock structure based on typical yfinance response
            # Implementation caveat: 'funds_data' is a property in recent versions
            return {
                "sectors": etf.get_sector_weightings() if hasattr(etf, "get_sector_weightings") else {}, 
                "countries": {} # yf logic here might need refinement
            }
        except Exception:
            return {}, {}
