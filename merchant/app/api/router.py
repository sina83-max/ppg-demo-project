"""Merchant API layer: thin routers, no business logic (docs/AGENTS.md section 3).

Endpoints defined here follow docs/api-contracts.md section 2. Every handler
only parses the request, delegates to `PurchaseService` via dependencies and
renders/returns the result.
"""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.schemas import PurchaseCreate

# TODO: import the service dependency from `app.dependencies` once it exists.
# TODO: import the Jinja2Templates instance from `app.main` (or extract it to
#       a small `app/templating.py` helper to avoid a circular import).

router = APIRouter()


@router.get("/health", tags=["ops"])
async def health() -> dict[str, Any]:
    """Liveness probe used by Docker Compose.

    Returns:
        dict[str, Any]: Static health payload.
    """
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse, tags=["dashboard"])
async def dashboard(request: Request) -> HTMLResponse:
    """Render the dashboard: list of purchases with per-row actions.

    TODO: fetch purchases via `PurchaseService.list_purchases()` and render
    `templates/dashboard.html` with Alpine.js (docs/AGENTS.md section 9).

    Args:
        request: Incoming request, used for template rendering.

    Returns:
        HTMLResponse: Rendered dashboard.
    """
    raise NotImplementedError


@router.get("/purchases/new", response_class=HTMLResponse, tags=["dashboard"])
async def create_form(request: Request) -> HTMLResponse:
    """Render the create-purchase form.

    TODO: render `templates/create.html`.

    Args:
        request: Incoming request, used for template rendering.

    Returns:
        HTMLResponse: Rendered form page.
    """
    raise NotImplementedError


@router.post("/purchases", tags=["purchases"])
async def create_purchase(payload: PurchaseCreate) -> JSONResponse:
    """Create a purchase (dashboard form post or JSON).

    TODO: call `PurchaseService.create_purchase(...)` and redirect to the
    dashboard (or return the created purchase as JSON).

    Args:
        payload: Validated create-purchase body.

    Returns:
        JSONResponse: Created purchase or a redirect to the dashboard.
    """
    raise NotImplementedError


@router.post("/callback", tags=["purchases"])
async def callback(request: Request) -> JSONResponse:
    """Receive the form-urlencoded callback from PPG.

    TODO: read `await request.form()`, call
    `PurchaseService.handle_callback(...)` and always return 200 so PPG does
    not retry a callback we already processed (docs/flows.md section 3).

    Args:
        request: Incoming form-urlencoded request.

    Returns:
        JSONResponse: Callback result.
    """
    raise NotImplementedError


@router.post("/purchases/{local_id}/verify", tags=["purchases"])
async def verify_purchase(local_id: int) -> JSONResponse:
    """Trigger verification of a purchase.

    TODO: load the purchase via the service and call
    `PurchaseService.verify(purchase_id)`.

    Args:
        local_id: Local `purchases.id`.

    Returns:
        JSONResponse: Updated purchase and PPG result.
    """
    raise NotImplementedError


@router.post("/purchases/{local_id}/reverse", tags=["purchases"])
async def reverse_purchase(local_id: int) -> JSONResponse:
    """Trigger reversal of a purchase.

    TODO: load the purchase via the service and call
    `PurchaseService.reverse(...)`.

    Args:
        local_id: Local `purchases.id`.

    Returns:
        JSONResponse: Updated purchase and PPG result.
    """
    raise NotImplementedError


@router.post("/purchases/{local_id}/refresh", tags=["purchases"])
async def refresh_purchase(local_id: int) -> JSONResponse:
    """Refresh a purchase state from PPG (dashboard "Refresh" action).

    TODO: call `PurchaseService.refresh_status(...)`.

    Args:
        local_id: Local `purchases.id`.

    Returns:
        JSONResponse: Updated purchase.
    """
    raise NotImplementedError


@router.get("/api/purchases", tags=["json-api"])
async def list_purchases(state: str | None = None, limit: int = 50, offset: int = 0) -> JSONResponse:
    """Return local purchases as JSON.

    TODO: delegate to `PurchaseService.list_purchases(...)` and serialize with
    `PurchaseRead`.

    Args:
        state: Optional state filter.
        limit: Maximum rows.
        offset: Rows to skip.

    Returns:
        JSONResponse: List of local purchases.
    """
    raise NotImplementedError


@router.get("/api/purchases/{local_id}", tags=["json-api"])
async def get_purchase(local_id: int) -> JSONResponse:
    """Return a single local purchase as JSON.

    TODO: delegate to `PurchaseService.get_purchase(local_id)`.

    Args:
        local_id: Local `purchases.id`.

    Returns:
        JSONResponse: The purchase, 404 when missing.
    """
    raise NotImplementedError
