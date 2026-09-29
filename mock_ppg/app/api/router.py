"""Mock PPG v3 router – same paths as the real gateway (docs/api-contracts.md).

Endpoints (all under `/v3`):
- POST /tokens, POST /tokens/refresh
- POST /purchases, GET /purchases
- POST /purchases/{purchaseId}/verify
- POST /purchases/reverse
- GET /purchases/{purchaseId}/payments  (simulated PSP page, not under /v3)
"""

from typing import Any

from fastapi import APIRouter, Body, Query

from app.api.schemas import (
    CreatePurchaseRequest,
    ReverseRequest,
    TokenRefreshRequest,
    TokenRequest,
)
from app.config import settings

# TODO: import the shared `MockPurchaseService` instance from `app.main`.
# TODO: extract the `Authorization: Bearer ...` check into a small dependency
#       and return the real PPG error envelope on failure.

router = APIRouter(prefix="/v3")


# --- Token -----------------------------------------------------------------


@router.post("/tokens")
async def generate_token(payload: TokenRequest = Body(...)) -> dict[str, Any]:
    """Return a valid-looking token pair (accepts any key).

    TODO: ignore the credentials, generate a fake JWT-like access token and a
    refresh token, and remember them so `/tokens/refresh` works.

    Args:
        payload: `apiKey` / `secretKey`.

    Returns:
        dict[str, Any]: `TokenResponse`.
    """
    raise NotImplementedError


@router.post("/tokens/refresh")
async def refresh_token(payload: TokenRefreshRequest = Body(...)) -> dict[str, Any]:
    """Exchange a refresh token for a new token pair.

    TODO: validate the refresh token and return a fresh pair.

    Args:
        payload: `refreshToken`.

    Returns:
        dict[str, Any]: `TokenResponse`.
    """
    raise NotImplementedError


# --- Purchases -------------------------------------------------------------


@router.post("/purchases")
async def create_purchase(payload: CreatePurchaseRequest = Body(...)) -> dict[str, Any]:
    """Create a purchase and return the switching URL.

    TODO: delegate to `MockPurchaseService.create_purchase`.

    Args:
        payload: `CreatePurchaseDto`.

    Returns:
        dict[str, Any]: `PurchaseCreationResult`.
    """
    raise NotImplementedError


@router.get("/purchases")
async def filter_purchases(
    clientReferenceNumber: str | None = Query(default=None),
    state: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
) -> dict[str, Any]:
    """List purchases with optional filters.

    TODO: delegate to `MockPurchaseService.filter_purchases`.

    Args:
        clientReferenceNumber: Optional reference filter.
        state: Optional state filter.
        page: Page number.
        size: Page size.

    Returns:
        dict[str, Any]: Paginated purchases.
    """
    raise NotImplementedError


@router.post("/purchases/reverse")
async def reverse_purchase(payload: ReverseRequest = Body(...)) -> dict[str, Any]:
    """Reverse a purchase by id or client reference number.

    TODO: delegate to `MockPurchaseService.reverse_purchase`.

    Args:
        payload: `purchaseId` or `clientReferenceNumber`.

    Returns:
        dict[str, Any]: `ReverseResultDto`.
    """
    raise NotImplementedError


@router.post("/purchases/{purchase_id}/verify")
async def verify_purchase(purchase_id: int) -> dict[str, Any]:
    """Verify a purchase (only succeeds from `READY_TO_VERIFY`).

    TODO: delegate to `MockPurchaseService.verify_purchase`.

    Args:
        purchase_id: Synthetic purchase id.

    Returns:
        dict[str, Any]: `VerificationResultDto`.
    """
    raise NotImplementedError


@router.get("/purchases/{purchase_id}")
async def get_purchase(purchase_id: int) -> dict[str, Any]:
    """Return a single purchase.

    TODO: delegate to `MockPurchaseService.get_purchase`.

    Args:
        purchase_id: Synthetic purchase id.

    Returns:
        dict[str, Any]: Purchase details.
    """
    raise NotImplementedError


# --- Simulated PSP ---------------------------------------------------------

# NOTE: lives outside the `/v3` router because the merchant redirects the
# browser to it directly (see docs/api-contracts.md section 1).
paying_router = APIRouter()


@paying_router.get("/purchases/{purchase_id}/payments", include_in_schema=False)
async def psp_payments_page(purchase_id: int, outcome: str = "SUCCESSFUL") -> dict[str, Any]:
    """Fake PSP page: completes the payment and triggers the merchant callback.

    TODO: render a tiny HTML page with a "Pay" / "Fail" button, and on click
    call `MockPurchaseService.handle_switching(purchase_id, outcome)`.
    The `outcome` query parameter is the demo switch for success/failure.

    Args:
        purchase_id: Synthetic purchase id from `pspSwitchingUrl`.
        outcome: `SUCCESSFUL` or `FAILED`.

    Returns:
        dict[str, Any]: Rendered result data.
    """
    raise NotImplementedError


# TODO: add demo-only helpers (e.g. GET /mock/state) to inspect the in-memory store.

# Referenced so the settings import is not flagged as unused while the router
# is still a stub; remove once the handlers read settings.
_ = settings
