"""Mock PPG v3 router – same paths as the real gateway (docs/api-contracts.md).

Endpoints (all under `/v3`):
- POST /tokens, POST /tokens/refresh
- POST /purchases, GET /purchases
- POST /purchases/{purchaseId}/verify
- POST /purchases/reverse
- GET /purchases/{purchaseId}/payments  (simulated PSP page, not under /v3)
"""

from typing import Any

from fastapi import APIRouter, Body, Depends, Query

from app.api.schemas import (
    CreatePurchaseRequest,
    PurchaseCreationResult,
    ReverseRequest,
    TokenRefreshRequest,
    TokenRequest,
    TokenResponse,
)
from app.dependencies import (
    get_purchase_service,
    get_token_service,
    require_access_token,
)
from app.services.purchase_service import MockPurchaseService
from app.services.token_service import TokenService

router = APIRouter(prefix="/v3")


# --- Token -----------------------------------------------------------------


@router.post("/tokens", response_model=TokenResponse)
async def generate_token(
    payload: TokenRequest = Body(...),
    tokens: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """Return a token pair. Any credentials are accepted (AGENTS.md section 8).

    Args:
        payload: `apiKey` / `secretKey`.
        tokens: Token service for this request.

    Returns:
        TokenResponse: The minted pair.
    """
    return TokenResponse(**tokens.issue_token(payload.apiKey, payload.secretKey))


@router.post("/tokens/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest = Body(...),
    tokens: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """Exchange a refresh token for a new pair.

    Args:
        payload: `refreshToken`.
        tokens: Token service for this request.

    Returns:
        TokenResponse: A fresh pair.
    """
    return TokenResponse(**tokens.refresh_token(payload.refreshToken))


@router.post("/purchases", response_model=PurchaseCreationResult)
async def create_purchase(
    payload: CreatePurchaseRequest = Body(...),
    service: MockPurchaseService = Depends(get_purchase_service),
    _token: str = Depends(require_access_token),
) -> PurchaseCreationResult:
    """Create a purchase and return the switching URL.

    Args:
        payload: `CreatePurchaseDto`.
        service: Purchase service for this request.
        _token: Presented access token, validated by the dependency.

    Returns:
        PurchaseCreationResult: `purchaseId` and `pspSwitchingUrl`.
    """
    return PurchaseCreationResult(**await service.create_purchase(payload.model_dump()))


@router.get("/purchases", response_model=dict[str, Any])
async def filter_purchases(
    clientReferenceNumber: str | None = Query(default=None),
    state: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    service: MockPurchaseService = Depends(get_purchase_service),
    _token: str = Depends(require_access_token),
) -> dict[str, Any]:
    """List purchases with optional filters.

    TODO: delegate to `MockPurchaseService.filter_purchases`, mapping the
    `clientReferenceNumber` query parameter onto the repository's
    `client_reference_number` filter and slicing the result for `page`/`size`.

    Args:
        clientReferenceNumber: Optional reference filter.
        state: Optional state filter.
        page: Page number.
        size: Page size.
        service: Purchase service for this request.
        _token: Presented access token, validated by the dependency.

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
