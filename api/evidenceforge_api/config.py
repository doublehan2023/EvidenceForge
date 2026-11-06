import ssl
from dataclasses import dataclass
from functools import lru_cache

import certifi
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


@dataclass(frozen=True)
class AsyncDatabaseUrl:
    """An asyncpg-compatible URL and transport options."""

    url: str
    connect_args: dict[str, object]


def to_asyncpg_url(database_url: str) -> AsyncDatabaseUrl:
    """Convert standard libpq URLs, including Neon URLs, for asyncpg."""
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql", "postgresql+psycopg2"}:
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    ssl_mode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    connect_args: dict[str, object] = {}
    if ssl_mode in {"require", "verify-ca", "verify-full"}:
        connect_args["ssl"] = ssl.create_default_context(cafile=certifi.where())

    return AsyncDatabaseUrl(
        url=url.set(query=query).render_as_string(hide_password=False), connect_args=connect_args
    )


class Settings(BaseSettings):
    """Configuration supplied by environment variables only."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    database_url_unpooled: str | None = None
    aws_endpoint_url: str | None = None
    aws_region: str = "us-east-1"
    s3_bucket: str
    sqs_queue_name: str
    api_port: int = 8000

    @property
    def migration_database_url(self) -> str:
        """Prefer Neon's direct connection for Alembic and admin operations."""
        return self.database_url_unpooled or self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
