"""In-memory store for the mock PPG (ADR-005 – no database).

Simple dict keyed by `purchase_id` is enough
(docs/data-model.md "Mock PPG In-Memory Model").
"""

from datetime import datetime, timezone
from typing import Any, Optional


class PurchaseStore:
    """Dictionary-backed purchase storage."""

    def __init__(self) -> None:
        """Initialize the empty in-memory store."""
        self._purchases: dict[int, dict[str, Any]] = {}
        self._next_id: int = 1000

    def next_purchase_id(self) -> int:
        """Return the next synthetic `purchaseId`.

        Returns:
            int: Monotonically increasing purchase id.
        """
        self._next_id += 1
        return self._next_id

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Insert a purchase in state `IN_PROGRESS`.

        TODO: build the stored record (amount, wage, currency, state,
        callbackUrl, clientReferenceNumber, createdAt, …).

        Args:
            payload: `CreatePurchaseDto` received from the merchant.

        Returns:
            dict[str, Any]: The stored purchase record.
        """
        raise NotImplementedError

    def get(self, purchase_id: int) -> Optional[dict[str, Any]]:
        """Fetch a purchase by id.

        Args:
            purchase_id: Synthetic purchase id.

        Returns:
            Optional[dict[str, Any]]: Stored record or None.
        """
        # TODO: return `self._purchases.get(purchase_id)`.
        raise NotImplementedError

    def get_by_client_reference_number(
        self, client_reference_number: str
    ) -> Optional[dict[str, Any]]:
        """Fetch a purchase by client reference number.

        Args:
            client_reference_number: Merchant reference.

        Returns:
            Optional[dict[str, Any]]: Stored record or None.
        """
        # TODO: linear scan over `self._purchases.values()`.
        raise NotImplementedError

    def set_state(self, purchase_id: int, state: str) -> Optional[dict[str, Any]]:
        """Update the state of a purchase.

        TODO: set `state` and `updatedAt`.

        Args:
            purchase_id: Synthetic purchase id.
            state: New state value.

        Returns:
            Optional[dict[str, Any]]: Updated record or None.
        """
        # TODO: implement.
        raise NotImplementedError

    def update(self, purchase_id: int, values: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Partially update a purchase record.

        TODO: merge `values` into the stored dict.

        Args:
            purchase_id: Synthetic purchase id.
            values: Fields to overwrite.

        Returns:
            Optional[dict[str, Any]]: Updated record or None.
        """
        # TODO: implement.
        raise NotImplementedError

    def filter(self, **params: Any) -> list[dict[str, Any]]:
        """Filter purchases for `GET /v3/purchases`.

        TODO: support `clientReferenceNumber`, `state`, `from`/`to` paging.

        Args:
            **params: Query filters.

        Returns:
            list[dict[str, Any]]: Matching records.
        """
        # TODO: implement.
        raise NotImplementedError

    def clear(self) -> None:
        """Drop all stored purchases (demo helper)."""
        self._purchases.clear()
        self._next_id = 1000

    @staticmethod
    def now() -> str:
        """Return the current UTC timestamp in ISO-8601.

        Returns:
            str: ISO-8601 timestamp.
        """
        return datetime.now(timezone.utc).isoformat()
