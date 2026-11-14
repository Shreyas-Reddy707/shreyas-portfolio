import os
import sys
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models."""


_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "hide_parameters": True,
    "pool_pre_ping": True,
}
if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules:
    _engine_kwargs["poolclass"] = NullPool
    _engine_kwargs.pop("pool_pre_ping", None)

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request."""
    async with AsyncSessionLocal() as session:
        yield session

