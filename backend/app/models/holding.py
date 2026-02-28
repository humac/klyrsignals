"""
Holding model - represents a single portfolio position
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal


class Holding(BaseModel):
    """
    Represents a single holding in a portfolio.
    """
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Ticker symbol (e.g., AAPL, MSFT)",
        examples=["AAPL"]
    )
    quantity: float = Field(
        ...,
        gt=0,
        description="Number of shares/units",
        examples=[50.0]
    )
    purchase_price: float = Field(
        ...,
        gt=0,
        description="Price per share at purchase (USD)",
        examples=[150.00]
    )
    purchase_date: Optional[date] = Field(
        None,
        description="Date of purchase",
        examples=["2024-01-15"]
    )
    asset_class: Literal["stock", "etf", "crypto", "mutual_fund"] = Field(
        "stock",
        description="Asset class category",
        examples=["stock"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 50,
                "purchase_price": 150.00,
                "purchase_date": "2024-01-15",
                "asset_class": "stock"
            }
        }
