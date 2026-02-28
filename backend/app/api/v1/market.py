"""
Market data endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

router = APIRouter(tags=["market"])


@router.get("/api/v1/prices")
async def get_prices(symbols: str = Query(..., description="Comma-separated list of ticker symbols")):
    """
    Get current market prices for multiple symbols.
    
    - **symbols**: Comma-separated list of ticker symbols (e.g., AAPL,MSFT,GOOGL)
    - **Returns**: Current prices for all symbols
    """
    try:
        import yfinance as yf
        
        symbol_list = [s.strip() for s in symbols.split(",")]
        prices = {}
        
        for symbol in symbol_list:
            try:
                ticker = yf.Ticker(symbol)
                # Use fast_info for quicker access
                info = ticker.fast_info
                if info and 'last_price' in info:
                    prices[symbol] = float(info['last_price'])
                else:
                    # Fallback to history
                    hist = ticker.history(period='1d')
                    if len(hist) > 0:
                        prices[symbol] = float(hist['Close'].iloc[-1])
                    else:
                        prices[symbol] = None
            except Exception as e:
                prices[symbol] = None
        
        return {
            "prices": prices,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "yfinance",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {str(e)}")


@router.get("/api/v1/prices/{symbol}")
async def get_price(symbol: str):
    """
    Get current market price for a single symbol.
    
    - **symbol**: Ticker symbol (e.g., AAPL)
    - **Returns**: Current price
    """
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        if info and 'last_price' in info:
            price = float(info['last_price'])
        else:
            hist = ticker.history(period='1d')
            if len(hist) > 0:
                price = float(hist['Close'].iloc[-1])
            else:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "yfinance",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price: {str(e)}")
