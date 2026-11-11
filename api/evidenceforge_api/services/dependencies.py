from dataclasses import dataclass

import boto3
from botocore.config import Config
from sqlalchemy import text

from evidenceforge_api.config import Settings
from evidenceforge_api.db.session import get_engine


@dataclass(frozen=True)
class DependencyStatus:
    database: bool
    object_storage: bool
    queue: bool

    @property
    def healthy(self) -> bool:
        return self.database and self.object_storage and self.queue


def _aws_client(service_name: str, settings: Settings):  # type: ignore[no-untyped-def]
    if settings.aws_endpoint_url is None:
        return boto3.client(
            service_name,
            region_name=settings.aws_region,
            config=Config(retries={"max_attempts": 1}),
        )
    return boto3.client(
        service_name,
        endpoint_url=settings.aws_endpoint_url,
        region_name=settings.aws_region,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 1}),
    )


async def check_database() -> bool:
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_object_storage(settings: Settings) -> bool:
    try:
        _aws_client("s3", settings).head_bucket(Bucket=settings.s3_bucket)
        return True
    except Exception:
        return False


def check_queue(settings: Settings) -> bool:
    try:
        _aws_client("sqs", settings).get_queue_url(QueueName=settings.sqs_queue_name)
        return True
    except Exception:
        return False


async def check_dependencies(settings: Settings) -> DependencyStatus:
    return DependencyStatus(
        database=await check_database(),
        object_storage=check_object_storage(settings),
        queue=check_queue(settings),
    )
