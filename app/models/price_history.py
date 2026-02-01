"""Price history model (TimescaleDB hypertable)."""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=lambda: datetime.now(timezone.utc),
    )
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    close_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
