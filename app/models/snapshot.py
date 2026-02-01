"""Net worth snapshot model (TimescaleDB hypertable)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NetWorthSnapshot(Base):
    __tablename__ = "net_worth_snapshots"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=lambda: datetime.now(timezone.utc),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    total_assets_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_liabilities_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    net_worth_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    breakdown_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
