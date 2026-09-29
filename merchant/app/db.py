"""SQLAlchemy async engine, session factory and declarative base.

Only the repository layer is allowed to use these objects.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# TODO: add pool / connection args if the project ever moves to PostgreSQL.

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
)

SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all merchant ORM models."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and close it afterwards.

    Yields:
        AsyncSession: Session bound to the configured async engine.
    """
    async with SessionFactory() as session:
        yield session


async def init_db() -> None:
    """Create all tables on startup (demo only; no migrations in scope)."""
    # Importing the models registers them on `Base.metadata`.
    from app.models import purchase  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()
