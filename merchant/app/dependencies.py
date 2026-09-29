"""FastAPI dependency providers.

Each provider returns one collaborator for the API layer, so routers never
build services/repositories/clients themselves.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.ppg_client import PPGClient
from app.db import get_session
from app.repositories.purchase_repository import PurchaseRepository
from app.services.purchase_service import PurchaseService

# TODO: provide the lifespan-managed shared `PPGClient` (see `main.py`).
# TODO: provide any dashboard-form dependencies here as well.

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_purchase_repository(session: SessionDep) -> PurchaseRepository:
    """Build a `PurchaseRepository` for the current request.

    Args:
        session: Request-scoped database session.

    Returns:
        PurchaseRepository: Repository bound to the request session.
    """
    return PurchaseRepository(session)


# TODO: implement `get_ppg_client() -> PPGClient` returning the instance created
#       in the app lifespan (`app.state.ppg_client`).
def get_ppg_client() -> PPGClient:
    """Return the shared PPGClient created during application startup.

    Returns:
        PPGClient: The lifespan-managed upstream client.
    """
    raise NotImplementedError


# TODO: wire this provider into the routers (see `app/api/router.py`).
def get_purchase_service(
    repository: Annotated[PurchaseRepository, Depends(get_purchase_repository)],
    ppg_client: Annotated[PPGClient, Depends(get_ppg_client)],
) -> PurchaseService:
    """Build a `PurchaseService` for the current request.

    Args:
        repository: Request-scoped repository.
        ppg_client: Shared upstream PPG client.

    Returns:
        PurchaseService: Service used by the routers.
    """
    return PurchaseService(repository, ppg_client)
