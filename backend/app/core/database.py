import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def wait_for_db(retries: int = 15, delay: float = 2.0) -> None:
    """Wait until DB is reachable."""
    import asyncpg

    raw_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    for attempt in range(1, retries + 1):
        try:
            conn = await asyncpg.connect(raw_url, ssl=False, timeout=5)
            await conn.execute("SELECT 1")
            await conn.close()
            logger.info("Database connection established.")
            return
        except Exception as exc:
            logger.warning("DB not ready (attempt %d/%d): %s: %s", attempt, retries, type(exc).__name__, exc)
            if attempt < retries:
                await asyncio.sleep(delay)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
