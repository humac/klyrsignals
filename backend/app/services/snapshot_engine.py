from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import Asset, AssetHolding, NetWorthSnapshot, AssetType
from app.services.market_data import MarketDataService
import json

class SnapshotEngine:
    @staticmethod
    def take_snapshot(db: Session) -> NetWorthSnapshot:
        """
        Calculates the current net worth of the portfolio and saves a snapshot.
        """
        assets = db.query(Asset).all()
        
        total_assets = 0
        total_liabilities = 0
        breakdown = {
            "sectors": {},
            "geography": {},
            "asset_class": {
                "liquid": 0,
                "fixed": 0
            }
        }

        for asset in assets:
            asset_value_cents = 0

            if asset.type == AssetType.LIQUID:
                # Sum up holdings
                holdings_value = 0
                for holding in asset.holdings:
                    # Get price (Cents)
                    # For snapshot, we want SLIGHTLY lagging but fast data 
                    # (MarketDataService handles cache)
                    price_df = MarketDataService.get_price_history(holding.ticker, db)
                    
                    if not price_df.empty:
                        # Use latest price
                        latest_price = price_df.iloc[-1]['close_cents']
                        # Qty is Decimal, Price is Int. Result is Int (Cents).
                        holding_val = int(holding.qty * latest_price)
                        holdings_value += holding_val
                        
                asset_value_cents = holdings_value
                breakdown["asset_class"]["liquid"] += holdings_value

            elif asset.type in [AssetType.FIXED, AssetType.BUSINESS, AssetType.CRYPTO]:
                # Read manual valuation from attributes
                # Expecting attributes['valuation_cents']
                # If missing, 0
                val = asset.attributes.get('valuation_cents', 0)
                asset_value_cents = int(val)
                breakdown["asset_class"]["fixed"] += asset_value_cents

            elif asset.type == AssetType.LIABILITY:
                # Liabilties are usually manually tracked loan balances
                val = asset.attributes.get('balance_cents', 0)
                asset_value_cents = int(val) # Positive number treated as liability magnitude
                total_liabilities += asset_value_cents

            # Add to totals (if not liability)
            if asset.type != AssetType.LIABILITY:
                total_assets += asset_value_cents

        # Create Snapshot
        snapshot = NetWorthSnapshot(
            timestamp=datetime.now(timezone.utc),
            total_assets_cents=total_assets,
            total_liabilities_cents=total_liabilities,
            total_equity_cents=total_assets - total_liabilities,
            breakdown=breakdown
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        return snapshot
