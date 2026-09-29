"""Mock behavior for the PPG v3 purchase lifecycle.

Rules come from docs/AGENTS.md section 8:
- create -> `purchaseId` + `pspSwitchingUrl`
- switching URL -> `READY_TO_VERIFY` + form-urlencoded callback to the merchant
- verify succeeds only from `READY_TO_VERIFY`
- reverse -> `REVERSED`
- `UNKNOWN` can be returned occasionally to demo retry logic
"""

import logging
from typing import Any, Optional

import httpx

from app.config import settings
from app.repositories.purchase_store import PurchaseStore

logger = logging.getLogger(__name__)


class MockPurchaseService:
    """Simulates the PPG purchase state machine and callbacks."""

    def __init__(self, store: PurchaseStore) -> None:
        """Store the in-memory purchase store.

        Args:
            store: In-memory purchase storage.
        """
        self._store = store

    # --- Purchases -----------------------------------------------------

    async def create_purchase(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a purchase and return `PurchaseCreationResult`.

        TODO: validate required fields (amount, currency, callbackUrl,
        clientReferenceNumber), store the record in `IN_PROGRESS` and return
        `{"purchaseId": ..., "pspSwitchingUrl": ...}`.

        Args:
            payload: `CreatePurchaseDto` from the merchant.

        Returns:
            dict[str, Any]: `PurchaseCreationResult`.
        """
        # TODO: implement.
        raise NotImplementedError

    async def handle_switching(self, purchase_id: int, outcome: str = "SUCCESSFUL") -> dict[str, Any]:
        """Simulate the user completing payment on the PSP page.

        TODO: move the purchase to `READY_TO_VERIFY`, POST the
        form-urlencoded callback to the stored `callbackUrl` and return the
        rendered result page data (docs/flows.md section 2).

        Args:
            purchase_id: Synthetic purchase id from the switching URL.
            outcome: `SUCCESSFUL` or `FAILED` for the demo.

        Returns:
            dict[str, Any]: Data used to render the fake PSP result page.
        """
        # TODO: implement + call `send_callback`.
        raise NotImplementedError

    async def verify_purchase(self, purchase_id: int) -> dict[str, Any]:
        """Verify a purchase.

        TODO: only succeed when state is `READY_TO_VERIFY`; return
        `SUCCESSFUL` / `FAILED` / `ALREADY_VERIFIED` / `NOT_VERIFIABLE` /
        `UNKNOWN` and honor `settings.unknown_answer_rate`.

        Args:
            purchase_id: Synthetic purchase id.

        Returns:
            dict[str, Any]: `VerificationResultDto`.
        """
        # TODO: implement.
        raise NotImplementedError

    async def reverse_purchase(
        self,
        purchase_id: Optional[int] = None,
        client_reference_number: Optional[str] = None,
    ) -> dict[str, Any]:
        """Reverse a purchase.

        TODO: return `SUCCESSFUL` / `ALREADY_REVERSED` / `NOT_REVERSIBLE` /
        `FAILED` / `UNKNOWN` and set the state to `REVERSED` on success.

        Args:
            purchase_id: Synthetic purchase id, if given.
            client_reference_number: Merchant reference, as alternative key.

        Returns:
            dict[str, Any]: `ReverseResultDto`.
        """
        # TODO: implement.
        raise NotImplementedError

    async def get_purchase(self, purchase_id: int) -> dict[str, Any]:
        """Return a single purchase.

        Args:
            purchase_id: Synthetic purchase id.

        Returns:
            dict[str, Any]: Purchase details.
        """
        # TODO: implement, 404 when unknown.
        raise NotImplementedError

    async def filter_purchases(self, **params: Any) -> dict[str, Any]:
        """Return paginated purchases for `GET /v3/purchases`.

        Args:
            **params: Query filters (clientReferenceNumber, state, page, size).

        Returns:
            dict[str, Any]: Paginated purchases payload.
        """
        # TODO: implement via `PurchaseStore.filter`.
        raise NotImplementedError

    # --- Callbacks -----------------------------------------------------

    async def send_callback(self, purchase_id: int, data: dict[str, Any]) -> None:
        """POST the callback payload to the merchant's `callbackUrl`.

        TODO: build the form-urlencoded fields from docs/api-contracts.md
        section 4 and `POST` them with httpx. Failures are logged only – the
        merchant may recover with an inquiry.

        Args:
            purchase_id: Synthetic purchase id.
            data: Fields to send (`status`, `amount`, `wage`, `pspName`, …).
        """
        # TODO: implement with `httpx.AsyncClient(timeout=settings.callback_timeout_seconds)`.
        raise NotImplementedError
