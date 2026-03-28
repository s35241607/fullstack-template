from collections.abc import AsyncGenerator
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


engine = create_async_engine(
    settings.db_url,
    echo=settings.db_echo,
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
    """Wait until DB is reachable using raw asyncpg (avoids pool/SSL issues on first connect)."""
    import asyncpg  # noqa: PLC0415

    # Extract host/port/db/user/password from the SQLAlchemy URL
    raw_url = settings.db_url.replace("postgresql+asyncpg://", "postgresql://")

    for attempt in range(1, retries + 1):
        try:
            conn = await asyncpg.connect(raw_url, ssl=False, timeout=5)
            await conn.execute("SELECT 1")
            await conn.close()
            logger.info("Database connection established.")
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("DB not ready (attempt %d/%d): %s: %s", attempt, retries, type(exc).__name__, exc)
            if attempt < retries:
                await asyncio.sleep(delay)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
