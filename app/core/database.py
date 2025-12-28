"""Database initialization and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.utils.snowflake import init_snowflake

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_database() -> None:
    """Initialize database engine, session factory and snowflake generator."""
    global engine, async_session_factory
    init_snowflake()
    engine = create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
    )
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)


async def close_database() -> None:
    """Close database connections."""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    if async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first.")
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
