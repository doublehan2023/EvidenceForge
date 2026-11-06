from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration supplied by environment variables only."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    aws_endpoint_url: str | None = None
    aws_region: str = "us-east-1"
    s3_bucket: str
    sqs_queue_name: str
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
