"""SQLAlchemy ORM model for the merchant's local copy of a purchase.

Field list follows docs/data-model.md. A local copy exists so the dashboard
keeps working when PPG is unreachable (ADR-006).
"""

from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PurchaseState(StrEnum):
    """Local purchase states (see docs/data-model.md)."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    READY_TO_VERIFY = "READY_TO_VERIFY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REVERSED = "REVERSED"
    UNKNOWN = "UNKNOWN"
    MANUALLY_SUCCESS = "MANUALLY_SUCCESS"


class Purchase(Base):
    """A purchase as tracked by the merchant."""

    __tablename__ = "purchases"
    __table_args__ = (
        Index("ix_purchases_purchase_id", "purchase_id"),
        Index("ix_purchases_state", "state"),
    )

    # Local identity
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # PPG identity
    purchase_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    purchase_id_str: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    client_reference_number: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )

    # Money
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    wage: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="IRR", server_default="IRR")

    # State
    state: Mapped[str] = mapped_column(
        String(32), nullable=False, default=PurchaseState.CREATED, server_default=PurchaseState.CREATED
    )

    # URLs
    callback_url: Mapped[str] = mapped_column(String(512), nullable=False)
    psp_switching_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Optional create-purchase fields
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    user_identifier: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Filled from callback / inquiry
    psp_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    psp_reference_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    psp_rrn: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payer_masked_card: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fail_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Raw callback payload, kept for debugging (see docs/data-model.md)
    raw_callback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """Return a short debug representation.

        Returns:
            str: Debug string of the purchase.
        """
        return (
            f"<Purchase id={self.id} purchase_id={self.purchase_id} "
            f"ref={self.client_reference_number!r} state={self.state!r}>"
        )
