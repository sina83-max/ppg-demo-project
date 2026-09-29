"""SQLAlchemy ORM model for a purchase held by the mock gateway.

SQLite (ADR-008) is what makes two real-gateway behaviours testable: rejecting
a duplicate `clientReferenceNumber` is now a UNIQUE constraint instead of a
comment, and `GET /v3/purchases` pages with real SQL.

Columns are snake_case; the camelCase PPG wire format is produced by
`MockPurchaseService.to_wire()` -- the same separation the merchant uses.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    """Return naive UTC, the form SQLite round-trips safely.

    SQLite does not persist tzinfo, so a value written as UTC-aware comes back
    naive. Writing naive UTC from the start keeps every later comparison
    (expiry checks, sorting) from mixing aware and naive datetimes.

    Returns:
        datetime: Naive UTC timestamp.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PurchaseState(StrEnum):
    """Purchase states the mock exposes, matching the real gateway."""

    IN_PROGRESS = "IN_PROGRESS"
    READY_TO_VERIFY = "READY_TO_VERIFY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REVERSED = "REVERSED"
    UNKNOWN = "UNKNOWN"


class Purchase(Base):
    """A purchase record created through the mock PPG API."""

    __tablename__ = "purchases"
    __table_args__ = (
        Index("ix_mock_purchases_purchase_id", "purchase_id", unique=True),
        Index("ix_mock_purchases_state", "state"),
    )

    # Surrogate key of the mock's own table; never sent on the wire.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The id the merchant receives as `purchaseId` and later calls back with.
    purchase_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    # The merchant's own reference. UNIQUE reproduces the real gateway's
    # "duplicate clientReferenceNumber" rejection.
    client_reference_number: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    wage: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    currency: Mapped[str] = mapped_column(
        String(8), nullable=False, default="IRR", server_default="IRR"
    )

    state: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=PurchaseState.IN_PROGRESS,
        server_default=PurchaseState.IN_PROGRESS,
    )

    callback_url: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    user_identifier: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
