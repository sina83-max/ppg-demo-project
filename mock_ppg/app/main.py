"""FastAPI entrypoint for the mock PPG service.

Skeleton only: the app boots and exposes `/health`. Token, purchase and
switching behavior is implemented in the next phase (TODOs in
`app/api/router.py`, `app/services/` and `app/repositories/`).
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.router import paying_router, router as v3_router
from app.config import settings
from app.repositories.purchase_store import PurchaseStore
from app.services.purchase_service import MockPurchaseService

logger = logging.getLogger(__name__)

store = PurchaseStore()
# TODO: build the service in the lifespan once the store is ready.
service = MockPurchaseService(store)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup/shutdown logging.

    TODO: reset the in-memory store on startup so every demo session starts
    from a clean state.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is handed back to the server while the app runs.
    """
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Starting %s (mock PPG, in-memory state)", settings.app_name)
    try:
        yield
    finally:
        store.clear()
        logger.info("Mock PPG stopped")


app = FastAPI(
    title=settings.app_name,
    description="Behavioral mock of Jibit PPG v3 (no credentials required).",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(v3_router)
app.include_router(paying_router)


@app.get("/health", tags=["ops"])
async def health() -> JSONResponse:
    """Liveness probe used by Docker Compose.

    Returns:
        JSONResponse: Static health payload.
    """
    return JSONResponse({"status": "ok", "service": "mock-ppg"})
