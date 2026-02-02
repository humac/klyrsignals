from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, BigInteger, DECIMAL, func, Text, JSON, Uuid
from sqlalchemy.orm import relationship
import uuid
import enum
from .database import Base
from datetime import datetime

class AssetType(enum.Enum):
    LIQUID = "LIQUID"
    FIXED = "FIXED"
    BUSINESS = "BUSINESS"
    CRYPTO = "CRYPTO"
    LIABILITY = "LIABILITY"

class ProviderType(enum.Enum):
    MANUAL = "MANUAL"
    SNAPTRADE = "SNAPTRADE"
    PLAID = "PLAID"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(Enum(AssetType), nullable=False)
    provider_type = Column(Enum(ProviderType), default=ProviderType.MANUAL)
    currency = Column(String, default="CAD")
    
    # Flexible metadata (e.g., address, bank_name, proxy_ticker)
    attributes = Column(JSON, default={})
    
    # Encrypted Access Token (stored as string, encryption handled in service layer)
    # We explicitly note this column should NEVER hold raw tokens
    access_token_enc = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    holdings = relationship("AssetHolding", back_populates="asset", cascade="all, delete-orphan")

class AssetHolding(Base):
    __tablename__ = "asset_holdings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(Uuid(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    
    ticker = Column(String, nullable=False) # e.g. "VFV.TO" or "CASH-CAD"
    qty = Column(DECIMAL, nullable=False)
    
    # Metadata for the holding (avg_cost_cents, etc.)
    metadata_json = Column(JSON, default={})
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    asset = relationship("Asset", back_populates="holdings")

class NetWorthSnapshot(Base):
    __tablename__ = "net_worth_snapshots"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    total_assets_cents = Column(BigInteger, nullable=False)
    total_liabilities_cents = Column(BigInteger, nullable=False)
    total_equity_cents = Column(BigInteger, nullable=False)
    
    # Snapshot of the breakdown (Sector %s, Geo %s) for time-travel analysis
    breakdown = Column(JSON, nullable=True)

class TickerPriceHistory(Base):
    __tablename__ = "ticker_price_history"
    
    # Composite PK logic typically preferred, but using UUID for simplicity + UniqueConstraint
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    ticker = Column(String, nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    close_cents = Column(BigInteger, nullable=False)
    
    # Optional: Volume, High, Low if needed later
    
    __table_args__ = (
        # Ensure one price per ticker per date
        {"unique_constraint": ("ticker", "date")},
    )
