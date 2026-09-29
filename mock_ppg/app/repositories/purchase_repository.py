"""SQL data access for the mock PPG (ADR-008 – SQLite).

The repository owns every SQL statement. Nothing above this layer knows the
storage is SQLite, which is what lets the mock swap in PostgreSQL later by
changing the URL alone (docs/data-model.md).

A repository instance is bound to one request's session and must not be shared.
"""

from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.purchase import Purchase, utcnow

# Mirrors the previous dict counter's starting point so ids stay familiar.
FIRST_PURCHASE_ID = 1000


class PurchaseRepository:
    """CRUD operations over the mock's `purchases` table."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to a request-scoped session.

        Args:
            session: Async session used for every statement below.
        """
        self._session = session

    async def next_purchase_id(self) -> int:
        """Return the next synthetic `purchaseId`.

        Derived from the current maximum rather than a held counter, so ids keep
        climbing across restarts instead of colliding with persisted rows.

        Returns:
            int: Next purchase id.
        """
        result = await self._session.execute(
            select(func.coalesce(func.max(Purchase.purchase_id), FIRST_PURCHASE_ID))
        )
        return int(result.scalar_one()) + 1

    async def create(self, values: dict[str, Any]) -> Purchase:
        """Insert a purchase and return the persisted row.

        Raises:
            IntegrityError: If `client_reference_number` already exists. The
                service layer turns this into the real gateway's rejection
                instead of a 500 -- a fidelity gain the dict version could not
                offer.
        """
        purchase = Purchase(**values)
        self._session.add(purchase)
        try:
            await self._session.commit()
        except IntegrityError:
            # The session is unusable after a failed commit; reset it so the
            # service can still read from it and report the conflict.
            await self._session.rollback()
            raise
        await self._session.refresh(purchase)
        return purchase

    async def get(self, purchase_id: int) -> Optional[Purchase]:
        """Fetch a purchase by the id the merchant was given.

        Args:
            purchase_id: The `purchaseId` from a create response.

        Returns:
            Optional[Purchase]: The row, or None if unknown.
        """
        result = await self._session.execute(
            select(Purchase).where(Purchase.purchase_id == purchase_id)
        )
        return result.scalar_one_or_none()

    async def get_by_client_reference_number(
        self, client_reference_number: str
    ) -> Optional[Purchase]:
        """Fetch a purchase by the merchant's reference.

        Args:
            client_reference_number: The merchant's `clientReferenceNumber`.

        Returns:
            Optional[Purchase]: The row, or None if unknown.
        """
        result = await self._session.execute(
            select(Purchase).where(
                Purchase.client_reference_number == client_reference_number
            )
        )
        return result.scalar_one_or_none()

    async def set_state(self, purchase_id: int, state: str) -> Optional[Purchase]:
        """Move a purchase to a new state and stamp `updated_at`.

        Args:
            purchase_id: The `purchaseId` to update.
            state: New state value.

        Returns:
            Optional[Purchase]: The updated row, or None if unknown.
        """
        return await self.update(purchase_id, {"state": state})

    async def update(
        self, purchase_id: int, values: dict[str, Any]
    ) -> Optional[Purchase]:
        """Apply a partial update and stamp `updated_at`.

        Args:
            purchase_id: The `purchaseId` to update.
            values: Column names to overwrite.

        Returns:
            Optional[Purchase]: The updated row, or None if unknown.
        """
        purchase = await self.get(purchase_id)
        if purchase is None:
            return None
        for key, value in values.items():
            setattr(purchase, key, value)
        purchase.updated_at = utcnow()
        await self._session.commit()
        return purchase

    async def filter(self, **params: Any) -> list[Purchase]:
        """Query purchases for `GET /v3/purchases`, newest id first.

        Args:
            **params: Optional `client_reference_number` and `state` filters.

        Returns:
            list[Purchase]: Matching rows, newest first.
        """
        statement = select(Purchase)

        reference = params.get("client_reference_number")
        if reference:
            statement = statement.where(
                Purchase.client_reference_number == reference
            )

        state = params.get("state")
        if state:
            statement = statement.where(Purchase.state == state)

        statement = statement.order_by(Purchase.purchase_id.desc())
        result = await self._session.execute(statement)
        return list(result.scalars().all())
