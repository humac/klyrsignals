"""
Market Data Service - Fetches prices from yfinance with caching
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional


class MarketDataService:
    """
    Service for fetching market data from Yahoo Finance.
    
    Implements caching to reduce API calls (15-minute TTL).
    """
    
    def __init__(self):
        self.cache: dict[str, tuple[float, datetime]] = {}
        self.cache_ttl = 900  # 15 minutes in seconds
    
    async def get_prices(self, symbols: list[str]) -> dict[str, Optional[float]]:
        """
        Get current prices for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            Dictionary mapping symbols to prices (None if not found)
        """
        prices = {}
        now = datetime.utcnow()
        
        for symbol in symbols:
            # Check cache first
            if symbol in self.cache:
                cached_price, cached_time = self.cache[symbol]
                if (now - cached_time).total_seconds() < self.cache_ttl:
                    prices[symbol] = cached_price
                    continue
            
            # Fetch from yfinance
            try:
                price = self._fetch_price(symbol)
                if price is not None:
                    self.cache[symbol] = (price, now)
                prices[symbol] = price
            except Exception:
                prices[symbol] = None
        
        return prices
    
    def _fetch_price(self, symbol: str) -> Optional[float]:
        """
        Fetch price for a single symbol from yfinance.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Current price or None if not found
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            
            if info and 'last_price' in info:
                return float(info['last_price'])
            
            # Fallback to history
            hist = ticker.history(period='1d')
            if len(hist) > 0:
                return float(hist['Close'].iloc[-1])
            
            return None
        except Exception:
            return None
    
    def clear_cache(self):
        """Clear the price cache"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached symbols"""
        return len(self.cache)


# Singleton instance
_market_data_service: Optional[MarketDataService] = None


def get_market_data_service() -> MarketDataService:
    """Get or create the market data service singleton"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service
