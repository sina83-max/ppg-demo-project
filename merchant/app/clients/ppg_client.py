"""The only component in the merchant that performs HTTP calls to PPG.

It works identically against the local `mock_ppg` and the real Jibit API;
the target is decided by `PPG_BASE_URL` + credentials from settings
(ADR-002, docs/AGENTS.md sections 7 and 11).

Method signatures below are fixed by docs/AGENTS.md section 7 and must not change.
"""

import logging
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TOKEN_PATH = "/v3/tokens"
TOKEN_REFRESH_PATH = "/v3/tokens/refresh"
PURCHASES_PATH = "/v3/purchases"
REVERSE_PATH = "/v3/purchases/reverse"


class PPGError(Exception):
    """Raised when PPG returns an error response.

    TODO: expose the PPG error `code` from docs/api-contracts.md section 5.
    """


class PPGClient:
    """Async HTTP client for the Jibit PPG v3 API (real or mock)."""

    def __init__(self) -> None:
        """Prepare client state.

        TODO: build the shared `httpx.AsyncClient` from settings
        (base_url, timeout, auth) and the in-memory token cache.
        """
        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    # --- Lifecycle -----------------------------------------------------

    async def startup(self) -> None:
        """Open the underlying HTTP connection pool (call from app lifespan)."""
        # TODO: create `httpx.AsyncClient(base_url=settings.ppg_base_url, ...)`.
        raise NotImplementedError

    async def shutdown(self) -> None:
        """Close the underlying HTTP connection pool."""
        # TODO: `await self._client.aclose()`.
        raise NotImplementedError

    # --- Token handling ------------------------------------------------

    async def generate_token(self) -> dict[str, Any]:
        """Request a new access/refresh token pair.

        TODO: `POST /v3/tokens` with `{apiKey, secretKey}` from settings and
        cache the returned tokens.

        Returns:
            dict[str, Any]: `{"accessToken": ..., "refreshToken": ...}`.
        """
        # TODO: implement + log errors.
        raise NotImplementedError

    async def refresh_token(self) -> dict[str, Any]:
        """Exchange the refresh token for a new token pair.

        TODO: `POST /v3/tokens/refresh` with `{refreshToken}` and update cache.

        Returns:
            dict[str, Any]: `{"accessToken": ..., "refreshToken": ...}`.
        """
        # TODO: implement + log errors.
        raise NotImplementedError

    async def _auth_headers(self) -> dict[str, str]:
        """Return `Authorization: Bearer ...` headers, refreshing if needed.

        Returns:
            dict[str, str]: Headers for an authenticated request.
        """
        # TODO: generate token lazily, refresh on 401, raise `PPGError` on failure.
        raise NotImplementedError

    # --- Purchases (contract fixed by docs/AGENTS.md section 7) ---------

    async def create_purchase(self, payload: dict) -> dict:
        """Create a purchase on PPG.

        TODO: `POST /v3/purchases` with the `CreatePurchaseDto` payload and
        return `PurchaseCreationResult` as a plain dict.

        Args:
            payload: `CreatePurchaseDto` fields (see docs/api-contracts.md).

        Returns:
            dict: PPG creation result, e.g. `{"purchaseId": ..., "pspSwitchingUrl": ...}`.
        """
        # TODO: implement via httpx; raise `PPGError` with the PPG error code.
        raise NotImplementedError

    async def verify_purchase(self, purchase_id: int) -> dict:
        """Verify a purchase.

        TODO: `POST /v3/purchases/{purchase_id}/verify`.

        Args:
            purchase_id: PPG purchase identifier.

        Returns:
            dict: `VerificationResultDto` as a plain dict.
        """
        # TODO: implement via httpx.
        raise NotImplementedError

    async def reverse_purchase(
        self,
        purchase_id: int | None = None,
        client_reference_number: str | None = None,
    ) -> dict:
        """Reverse a purchase by id or by client reference number.

        TODO: `POST /v3/purchases/reverse` with
        `{"purchaseId": ...}` or `{"clientReferenceNumber": ...}`.

        Args:
            purchase_id: PPG purchase identifier, if known.
            client_reference_number: Merchant reference, as alternative key.

        Returns:
            dict: `ReverseResultDto` as a plain dict.
        """
        # TODO: implement via httpx.
        raise NotImplementedError

    async def get_purchase(self, purchase_id: int) -> dict:
        """Fetch a single purchase from PPG.

        TODO: `GET /v3/purchases/{purchase_id}`.

        Args:
            purchase_id: PPG purchase identifier.

        Returns:
            dict: Purchase details as a plain dict.
        """
        # TODO: implement via httpx.
        raise NotImplementedError

    async def filter_purchases(self, **params: Any) -> dict:
        """List/filter purchases on PPG.

        TODO: `GET /v3/purchases` with the given query parameters.

        Args:
            **params: Query filters supported by PPG (e.g. `clientReferenceNumber`, `state`).

        Returns:
            dict: Paginated purchases payload.
        """
        # TODO: implement via httpx.
        raise NotImplementedError
