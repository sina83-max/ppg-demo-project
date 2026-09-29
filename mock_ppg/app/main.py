"""FastAPI entrypoint for the mock PPG service.

The app boots, exposes `/health` and owns a SQLite file. Purchase state lives
in that database (ADR-008) rather than in process memory, so a `docker compose
restart` no longer wipes the demo's purchases. Endpoint behavior is still
staged (TODOs in `app/api/router.py` and `app/services/`).
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.router import paying_router, router as v3_router
from app.config import settings
from app.db import close_db, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the schema on startup and release the DB on shutdown.

    `init_db` is additive, so an existing `mock_ppg.db` is reused as-is. Use
    `docker compose down -v` (or delete the file) to start a demo from a clean
    slate.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is handed back to the server while the app runs.
    """
    logging.basicConfig(level=settings.log_level.upper())
    await init_db()
    logger.info("Started %s (SQLite at %s)", settings.app_name, settings.database_url)
    try:
        yield
    finally:
        await close_db()
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
