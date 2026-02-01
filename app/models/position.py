"""Holdings position model."""

import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, ForeignKey, BigInteger, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssetClass(str, enum.Enum):
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    CASH = "cash"
    CRYPTO = "crypto"
    OTHER = "other"


class Currency(str, enum.Enum):
    CAD = "CAD"
    USD = "USD"


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    asset_class: Mapped[AssetClass] = mapped_column(
        SAEnum(AssetClass, name="asset_class_enum"), default=AssetClass.EQUITY
    )
    units: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=0)
    cost_basis_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    market_value_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    currency: Mapped[Currency] = mapped_column(
        SAEnum(Currency, name="position_currency_enum"), default=Currency.CAD
    )
    exchange: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_price_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    account = relationship("Account", back_populates="positions")
    user = relationship("User", back_populates="positions")
