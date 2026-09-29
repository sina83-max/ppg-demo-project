"""FastAPI dependencies: session -> repository -> service.

Wiring is per request, not a module-level singleton. An AsyncSession belongs to
one task at a time, so a shared global session would break as soon as two
requests overlap. The service is cheap to build, so each request gets its own.
"""

from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.errors import ppg_error
from app.repositories.purchase_repository import PurchaseRepository
from app.services.purchase_service import MockPurchaseService
from app.services.token_service import TokenService

# auto_error=False so a missing header reaches our own handler and produces the
# PPG envelope, instead of Starlette's default 403 body.
bearer_scheme = HTTPBearer(auto_error=False)


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


def get_token_service() -> TokenService:
    """Return a token service.

    It holds no state, so building one per request costs nothing and keeps the
    "no module-level singletons" rule intact.

    Returns:
        TokenService: Token service for this request.
    """
    return TokenService()


async def require_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> str:
    """Require an `Authorization: Bearer <token>` header.

    The mock accepts any non-empty token, so this
    proves only that the client knows it must send the header -- which is exactly
    what we want to exercise before switching to the real gateway.

    Args:
        credentials: Parsed bearer credentials, or None when absent.

    Returns:
        str: The presented access token.

    Raises:
        PPGError: `auth.token_required` when the header is missing or empty.
    """
    if credentials is None or not credentials.credentials.strip():
        raise ppg_error(
            "auth.token_required",
            "An 'Authorization: Bearer <token>' header is required.",
            status_code=401,
        )
    return credentials.credentials