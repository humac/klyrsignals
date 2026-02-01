"""Sector/geographic weight enrichment cache."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SectorWeight(Base):
    __tablename__ = "sector_weights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(3), nullable=False)
    weight_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="yfinance")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
