"""FastAPI application entrypoint for the merchant service.

Skeleton only: the app boots, creates the SQLite schema and exposes `/health`.
Routers/templates and the business use cases land in the next phase
(see the TODO markers in `app/api/router.py` and `app/services/`).
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.api.router import router as api_router
from app.config import settings
from app.db import close_db, init_db

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup/shutdown resources.

    TODO: instantiate the shared `PPGClient` on startup, store it on
    `app.state` and await its `shutdown()` on exit (see app/clients/ppg_client.py).

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is handed back to the server while the app runs.
    """
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Starting %s (PPG_BASE_URL=%s)", settings.app_name, settings.ppg_base_url)
    await init_db()
    try:
        yield
    finally:
        await close_db()
        logger.info("Merchant stopped")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router)

# TODO: templates are wired in the router; move this instance to
#       `app/templating.py` to avoid a circular import between main and router.
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["alpinejs_cdn_url"] = settings.alpinejs_cdn_url
