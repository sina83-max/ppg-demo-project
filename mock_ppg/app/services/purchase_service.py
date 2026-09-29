"""Mock behavior for the PPG v3 purchase lifecycle.

Rules come from docs/AGENTS.md section 8:
- create -> `purchaseId` + `pspSwitchingUrl`
- switching URL -> `READY_TO_VERIFY` + form-urlencoded callback to the merchant
- verify succeeds only from `READY_TO_VERIFY`
- reverse -> `REVERSED`
- `UNKNOWN` can be returned occasionally to demo retry logic
"""

import logging
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlsplit, urlunsplit

import httpx
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.errors import ppg_error
from app.models.purchase import Purchase, PurchaseState
from app.repositories.purchase_repository import PurchaseRepository

logger = logging.getLogger(__name__)


def _iso(moment: datetime) -> str:
    """Render a naive-UTC timestamp as ISO-8601 with an explicit `Z`.

    Columns hold naive UTC because SQLite drops tzinfo
    (see `app/models/purchase.py`); the trailing `Z` restores the offset the
    real gateway would send.

    Args:
        moment: Naive UTC timestamp from the database.

    Returns:
        str: ISO-8601 timestamp.
    """
    return moment.isoformat() + "Z"


class MockPurchaseService:
    """Simulates the PPG purchase state machine and callbacks."""

    def __init__(self, repository: PurchaseRepository) -> None:
        """Store the repository used for all persistence.

        The service never sees a session; it only asks the repository. It does
        not own a repository either -- FastAPI builds one per request
        (app/dependencies.py), because the session underneath cannot be shared.

        Args:
            repository: SQL data access for the mock's `purchases` table.
        """
        self._repository = repository

    @staticmethod
    def to_wire(purchase: Purchase) -> dict[str, Any]:
        """Map an ORM row onto the camelCase PPG wire format.

        TODO: implement the snake_case -> camelCase mapping required by
        docs/api-contracts.md (purchase_id -> purchaseId,
        client_reference_number -> clientReferenceNumber, ...). Keeping the
        mapping in one place is what lets the columns stay snake_case.

        Args:
            purchase: The persisted row.

        Returns:
            dict[str, Any]: PPG-shaped payload.
        """
        return {
            "purchaseId": purchase.purchase_id,
            "clientReferenceNumber": purchase.client_reference_number,
            "amount": purchase.amount,
            "wage": purchase.wage,
            "currency": purchase.currency,
            "state": purchase.state,
            "callbackUrl": purchase.callback_url,
            "description": purchase.description,
            "userIdentifier": purchase.user_identifier,
            "createdAt": _iso(purchase.created_at),
            "updatedAt": _iso(purchase.updated_at),
        }

    @staticmethod
    def resolve_callback_url(callback_url: str) -> str:
        """Rewrite the callback host when running under Docker.

        The merchant builds `callbackUrl` from its browser-facing base
        (`http://localhost:8000`). That is correct for a browser and for the
        real Jibit PPG, but unreachable from inside this container, where
        "localhost" is the mock itself. Swapping in
        `settings.callback_base_url_override` fixes the mock without the
        merchant needing to know which gateway it is talking to, which is what
        keeps the environment switch to three variables
        (docs/AGENTS.md section 11).

        Args:
            callback_url: The URL the merchant sent.

        Returns:
            str: The URL the mock will actually POST to.
        """
        override = settings.callback_base_url_override.rstrip("/")
        if not override:
            return callback_url
        original = urlsplit(callback_url)
        return urlunsplit(
            (
                original.scheme,
                urlsplit(override).netloc,
                original.path,
                original.query,
                original.fragment,
            )
        )

    @staticmethod
    def build_switching_url(purchase_id: int) -> str:
        """Return the URL the browser is redirected to (the fake PSP page).

        Args:
            purchase_id: The id we just assigned.

        Returns:
            str: Absolute switching URL, based on the browser-facing base.
        """
        return (
            f"{settings.public_base_url.rstrip('/')}"
            f"/purchases/{purchase_id}/payments"
        )

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
        purchase_id = await self._repository.next_purchase_id()
        try:
            purchase = await self._repository.create(
                {
                    "purchase_id": purchase_id,
                    "client_reference_number": payload["clientReferenceNumber"],
                    "amount": payload["amount"],
                    "wage": payload.get("wage") or 0,
                    "currency": payload.get("currency") or "IRR",
                    "state": PurchaseState.IN_PROGRESS,
                    "callback_url": self.resolve_callback_url(payload["callbackUrl"]),
                    "description": payload.get("description"),
                    "user_identifier": payload.get("userIdentifier"),
                }
            )
        except IntegrityError:
            raise ppg_error(
                "purchase.duplicate_client_reference",
                f"clientReferenceNumber '{payload['clientReferenceNumber']}' "
                "has already been used.",
                status_code=409,
            ) from None

        return {
            "purchaseId": purchase.purchase_id,
            "pspSwitchingUrl": self.build_switching_url(purchase.purchase_id),
            "clientReferenceNumber": purchase.client_reference_number,
            "state": purchase.state,
        }

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
        # TODO: implement via `PurchaseRepository.filter` + `to_wire`.
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
