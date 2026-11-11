from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from evidenceforge_api.config import get_settings, to_asyncpg_url


@lru_cache
def get_engine() -> AsyncEngine:
    connection = to_asyncpg_url(get_settings().database_url)
    return create_async_engine(
        connection.url, connect_args=connection.connect_args, pool_pre_ping=True
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session
