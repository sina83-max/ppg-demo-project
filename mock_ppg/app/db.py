"""SQLAlchemy engine, session factory and schema bootstrap for the mock PPG.

The mock owns its own SQLite file (separate from the merchant's) so the demo
needs no shared database and the two services can be reset independently.
"""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base for the mock PPG's ORM models."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, creating it on first use.

    One engine per process is intentional: it owns the SQLite connection pool
    and must outlive individual requests.

    Returns:
        AsyncEngine: The shared async engine.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory bound to the shared engine.

    `expire_on_commit=False` keeps ORM objects readable after commit, so a
    repository can commit and still return the instance it just wrote.

    Returns:
        async_sessionmaker[AsyncSession]: The shared session factory.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one session per request and always release it.

    FastAPI dependency: one session per request, never shared globally, because
    an AsyncSession must not be used by two concurrent tasks.

    Yields:
        AsyncIterator[AsyncSession]: A request-scoped session.
    """
    async with get_session_factory()() as session:
        yield session


async def init_db() -> None:
    """Create the SQLite file and the `purchases` table if they are missing.

    Called once on startup. `create_all` is additive: it never drops or alters
    an existing table, so data survives container restarts.
    """
    # Import for the side effect of registering models on Base.metadata.
    from app.models import Purchase  # noqa: F401

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the engine on shutdown to release the SQLite file handle."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
