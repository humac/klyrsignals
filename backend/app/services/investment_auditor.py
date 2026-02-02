from sqlalchemy.orm import Session
from app.models import Asset, AssetType, AssetHolding
from app.services.market_data import MarketDataService
import pandas as pd

class InvestmentAuditor:
    @staticmethod
    def generate_look_through_analysis(db: Session, assets: list[Asset]):
        """
        Decomposes the portfolio into underlying exposures (Sector, Country).
        Returns a dictionary with 'sectors' and 'geography'.
        """
        total_exposure = {
            "sectors": {},
            "geography": {}
        }
        
        total_portfolio_value = 0

        for asset in assets:
            if asset.type == AssetType.LIQUID:
                for holding in asset.holdings:
                    # 1. Get current value
                    price_df = MarketDataService.get_price_history(holding.ticker, db)
                    if price_df.empty:
                        continue
                        
                    price = price_df.iloc[-1]['close_cents']
                    value = int(holding.qty * price)
                    total_portfolio_value += value
                    
                    # 2. Get Composition
                    comp = MarketDataService.get_etf_composition(holding.ticker)
                    
                    # 3. Allocating exposure
                    # Sectors
                    sectors = comp.get('sectors', {})
                    for sector, weight in sectors.items():
                        # weight is 0.0 to 1.0 usually (or 0-100 check yfinance)
                        # yfinance usually returns 0.25 for 25%? Need to verify. 
                        # Assuming 0.0-1.0 float here.
                        amount = value * weight
                        total_exposure["sectors"][sector] = total_exposure["sectors"].get(sector, 0) + amount

                    # Geography (Country) - If yf provides it
                    countries = comp.get('countries', {})
                    for country, weight in countries.items():
                        amount = value * weight
                        total_exposure["geography"][country] = total_exposure["geography"].get(country, 0) + amount

            elif asset.type in [AssetType.FIXED, AssetType.BUSINESS]:
                # Manual asset exposure
                # Residential Real Estate
                val = asset.attributes.get('valuation_cents', 0)
                total_portfolio_value += val
                
                # Assign sector based on manual logic or attributes
                # e.g. "Real Estate"
                sector = "Real Estate"
                total_exposure["sectors"][sector] = total_exposure["sectors"].get(sector, 0) + val
                
                # Assign Geo (Canada usually)
                country = "Canada"
                total_exposure["geography"][country] = total_exposure["geography"].get(country, 0) + val

        return total_exposure, total_portfolio_value

    @staticmethod
    def check_concentration_alerts(exposure: dict, total_value: int):
        """
        Checks for:
        - Single Country > 20% (excl. CA/US)
        - Single Sector > 25%
        - Home Bias (CA) > 60%
        """
        alerts = []
        
        # Avoid div by zero
        if total_value == 0:
            return []

        # Sector Check
        for sector, amount in exposure['sectors'].items():
            pct = amount / total_value
            if pct > 0.25:
                alerts.append(f"High Sector Concentration: {sector} is {pct*100:.1f}% (> 25%)")

        # Geo Check
        for country, amount in exposure['geography'].items():
            pct = amount / total_value
            
            if country == "Canada" and pct > 0.60:
                alerts.append(f"Home Bias Warning: Canada is {pct*100:.1f}% (> 60%)")
            
            elif country not in ["Canada", "United States"] and pct > 0.20:
                alerts.append(f"High Geographic Risk: {country} is {pct*100:.1f}% (> 20%)")
                
        return alerts

    @staticmethod
    def calculate_correlation_matrix(db: Session, assets: list[Asset]):
        """
        Calculates correlation between assets using 36-month price history.
        Uses proxy tickers for manual assets if available.
        """
        price_map = {}
        
        for asset in assets:
            ticker = None
            if asset.type == AssetType.LIQUID:
                # For simplicity, pick the largest holding or treat asset as a wrapper?
                # The prompt implies correlating specific holdings OR the asset if it has a proxy.
                # Let's iterate holdings for Liquid
                for h in asset.holdings:
                    price_map[f"{h.ticker}"] = MarketDataService.get_price_history(h.ticker, db)
            
            elif asset.attributes.get('proxy_ticker'):
                ticker = asset.attributes['proxy_ticker']
                price_map[f"{asset.name} ({ticker})"] = MarketDataService.get_price_history(ticker, db)

        # Build DataFrame
        combined_df = pd.DataFrame()
        
        for name, df in price_map.items():
            if df.empty:
                continue
            # Set index to date
            df = df.set_index('date')
            # Rename col
            df = df.rename(columns={'close_cents': name})
            # Join
            if combined_df.empty:
                combined_df = df[[name]]
            else:
                combined_df = combined_df.join(df[[name]], how='outer')

        # Calculate Correlation
        if combined_df.empty:
            return pd.DataFrame()
            
        corr_matrix = combined_df.corr()
        return corr_matrix
