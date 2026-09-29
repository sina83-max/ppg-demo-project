"""Repository for the local `purchases` table.

Pure data access: CRUD and queries only (docs/AGENTS.md section 3).
No business rules, no knowledge of PPG or HTTP.
"""

from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.purchase import Purchase, PurchaseState


class PurchaseRepository:
    """CRUD and query helpers for `Purchase`."""

    def __init__(self, session: AsyncSession) -> None:
        """Store the request-scoped session.

        Args:
            session: Async SQLAlchemy session.
        """
        self._session = session

    # --- Create --------------------------------------------------------

    async def create(self, values: dict[str, Any]) -> Purchase:
        """Insert a new purchase row.

        Args:
            values: Column values for the new row.

        Returns:
            Purchase: The persisted entity.
        """
        # TODO: implement insert + commit + refresh.
        raise NotImplementedError

    # --- Read ----------------------------------------------------------

    async def get_by_id(self, local_id: int) -> Optional[Purchase]:
        """Fetch a purchase by local primary key.

        Args:
            local_id: Local `purchases.id`.

        Returns:
            Optional[Purchase]: Purchase or None when missing.
        """
        # TODO: implement `select(Purchase).where(Purchase.id == local_id)`.
        raise NotImplementedError

    async def get_by_purchase_id(self, purchase_id: int) -> Optional[Purchase]:
        """Fetch a purchase by the PPG `purchaseId`.

        Args:
            purchase_id: Identifier returned by PPG.

        Returns:
            Optional[Purchase]: Purchase or None when missing.
        """
        # TODO: implement `select(Purchase).where(Purchase.purchase_id == purchase_id)`.
        raise NotImplementedError

    async def get_by_client_reference_number(
        self, client_reference_number: str
    ) -> Optional[Purchase]:
        """Fetch a purchase by its unique merchant-side reference.

        Args:
            client_reference_number: Unique reference per merchant.

        Returns:
            Optional[Purchase]: Purchase or None when missing.
        """
        # TODO: implement lookup by unique column.
        raise NotImplementedError

    async def list_purchases(
        self,
        *,
        state: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Purchase]:
        """List purchases for the dashboard / JSON API.

        Args:
            state: Optional state filter.
            limit: Maximum rows to return.
            offset: Rows to skip.

        Returns:
            Sequence[Purchase]: Matching rows, newest first.
        """
        # TODO: implement filtered select ordered by `id DESC`.
        raise NotImplementedError

    # --- Update --------------------------------------------------------

    async def update(
        self, local_id: int, values: dict[str, Any]
    ) -> Optional[Purchase]:
        """Update a purchase by local primary key.

        Args:
            local_id: Local `purchases.id`.
            values: Columns to write.

        Returns:
            Optional[Purchase]: The updated entity, or None when missing.
        """
        # TODO: implement load + assign + commit.
        raise NotImplementedError

    async def update_state(
        self,
        local_id: int,
        state: PurchaseState | str,
        *,
        verified_at: Optional[datetime] = None,
    ) -> Optional[Purchase]:
        """Update only the state (and optionally `verified_at`).

        Args:
            local_id: Local `purchases.id`.
            state: New state value.
            verified_at: Timestamp to set when a verify succeeded.

        Returns:
            Optional[Purchase]: The updated entity, or None when missing.
        """
        # TODO: implement partial `update()` statement.
        raise NotImplementedError

    async def save_raw_callback(
        self, local_id: int, raw_payload: str
    ) -> Optional[Purchase]:
        """Persist the raw callback payload for debugging.

        Args:
            local_id: Local `purchases.id`.
            raw_payload: Serialized form-urlencoded payload.

        Returns:
            Optional[Purchase]: The updated entity, or None when missing.
        """
        # TODO: implement via `update()`.
        raise NotImplementedError

    # --- Delete --------------------------------------------------------

    async def delete(self, local_id: int) -> bool:
        """Delete a purchase row.

        Args:
            local_id: Local `purchases.id`.

        Returns:
            bool: True when a row was removed.
        """
        # TODO: implement delete + commit.
        raise NotImplementedError

    # --- Misc ----------------------------------------------------------

    async def exists_by_client_reference_number(
        self, client_reference_number: str
    ) -> bool:
        """Check uniqueness of `client_reference_number`.

        Args:
            client_reference_number: Reference to test.

        Returns:
            bool: True when a row with this reference already exists.
        """
        # TODO: implement existence check.
        raise NotImplementedError
