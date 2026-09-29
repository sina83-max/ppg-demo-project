"""Business logic for the purchase lifecycle.

Create -> Callback -> Verify -> Reverse (see docs/flows.md).
This layer owns domain rules, state transitions and orchestration of
`PurchaseRepository` + `PPGClient`.
"""

from typing import Any, Optional

from app.clients.ppg_client import PPGClient
from app.models.purchase import Purchase
from app.repositories.purchase_repository import PurchaseRepository


class PurchaseService:
    """Use-case oriented service for purchases."""

    def __init__(
        self, repository: PurchaseRepository, ppg_client: PPGClient
    ) -> None:
        """Store the layer collaborators.

        Args:
            repository: Data access for the local `purchases` table.
            ppg_client: Upstream client for the real or mock PPG.
        """
        self._repository = repository
        self._ppg_client = ppg_client

    # --- Use cases -----------------------------------------------------

    async def create_purchase(
        self,
        *,
        amount: int,
        client_reference_number: str,
        wage: int = 0,
        currency: str = "IRR",
        description: Optional[str] = None,
        user_identifier: Optional[str] = None,
    ) -> Purchase:
        """Create a purchase on PPG and store the local copy.

        TODO: build `CreatePurchaseDto` (callbackUrl is added here, not by the
        router), call `PPGClient.create_purchase`, persist with state
        `CREATED` / `IN_PROGRESS` and store `psp_switching_url`.

        Args:
            amount: Amount in IRR.
            client_reference_number: Unique merchant reference.
            wage: Optional wage.
            currency: Currency, always `IRR` in this project.
            description: Optional description.
            user_identifier: Optional end-user identifier.

        Returns:
            Purchase: The locally stored purchase.
        """
        raise NotImplementedError

    async def handle_callback(self, form_data: dict[str, Any]) -> Optional[Purchase]:
        """Handle the form-urlencoded callback sent by PPG.

        TODO: locate the purchase by `purchaseId` or `clientReferenceNumber`,
        map `status` to a local state, store PSP fields and the raw payload
        (see docs/flows.md section 3).

        Args:
            form_data: Parsed form fields from PPG.

        Returns:
            Optional[Purchase]: Updated purchase, or None when unmatched.
        """
        raise NotImplementedError

    async def verify(self, purchase_id: int) -> Purchase:
        """Verify a purchase against PPG.

        TODO: call `PPGClient.verify_purchase` and map
        `SUCCESSFUL`/`FAILED`/`UNKNOWN`/`ALREADY_VERIFIED`/`NOT_VERIFIABLE`
        to local states, then set `verified_at`.

        Args:
            purchase_id: PPG purchase identifier.

        Returns:
            Purchase: Updated purchase.
        """
        raise NotImplementedError

    async def reverse(
        self,
        purchase_id: Optional[int] = None,
        client_reference_number: Optional[str] = None,
    ) -> Purchase:
        """Reverse a purchase.

        TODO: call `PPGClient.reverse_purchase`, map
        `SUCCESSFUL`/`ALREADY_REVERSED`/`NOT_REVERSIBLE`/`FAILED`/`UNKNOWN`
        to local states.

        Args:
            purchase_id: PPG purchase identifier, if known.
            client_reference_number: Merchant reference, as alternative key.

        Returns:
            Purchase: Updated purchase.
        """
        raise NotImplementedError

    async def refresh_status(self, purchase_id: int) -> Purchase:
        """Refresh the local state from PPG (dashboard "Refresh" button).

        TODO: call `PPGClient.get_purchase` and align the local row.

        Args:
            purchase_id: PPG purchase identifier.

        Returns:
            Purchase: Updated purchase.
        """
        raise NotImplementedError

    # --- Dashboard helpers ---------------------------------------------

    async def list_purchases(
        self, *, state: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> list[Purchase]:
        """List local purchases for the dashboard.

        Args:
            state: Optional state filter.
            limit: Maximum rows to return.
            offset: Rows to skip.

        Returns:
            list[Purchase]: Matching purchases, newest first.
        """
        # TODO: delegate to `PurchaseRepository.list_purchases`.
        raise NotImplementedError

    async def get_purchase(self, local_id: int) -> Optional[Purchase]:
        """Get a single local purchase.

        Args:
            local_id: Local `purchases.id`.

        Returns:
            Optional[Purchase]: Purchase or None when missing.
        """
        # TODO: delegate to `PurchaseRepository.get_by_id`.
        raise NotImplementedError
