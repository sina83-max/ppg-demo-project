"""FastAPI dependencies: session -> repository -> service.

Wiring is per request, not a module-level singleton. An AsyncSession belongs to
one task at a time, so a shared global session would break as soon as two
requests overlap. The service is cheap to build, so each request gets its own.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories.purchase_repository import PurchaseRepository
from app.services.purchase_service import MockPurchaseService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_purchase_repository(session: SessionDep) -> PurchaseRepository:
    """Build a repository bound to the request's session.

    Args:
        session: Request-scoped async session.

    Returns:
        PurchaseRepository: Repository for this request.
    """
    return PurchaseRepository(session)


def get_purchase_service(
    repository: Annotated[PurchaseRepository, Depends(get_purchase_repository)],
) -> MockPurchaseService:
    """Build a service for the request's repository.

    Args:
        repository: Request-scoped repository.

    Returns:
        MockPurchaseService: Service for this request.
    """
    return MockPurchaseService(repository)
