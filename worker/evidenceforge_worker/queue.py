import json
import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import boto3
from botocore.config import Config

from evidenceforge_worker.config import WorkerSettings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HealthcheckMessage:
    request_id: UUID
    sent_at: datetime


def parse_healthcheck_message(body: str) -> HealthcheckMessage:
    payload = json.loads(body)
    if payload.get("type") != "healthcheck":
        raise ValueError("unsupported message type")
    return HealthcheckMessage(
        request_id=UUID(payload["request_id"]), sent_at=datetime.fromisoformat(payload["sent_at"])
    )


def create_sqs_client(settings: WorkerSettings):  # type: ignore[no-untyped-def]
    if settings.aws_endpoint_url is None:
        return boto3.client(
            "sqs",
            region_name=settings.aws_region,
            config=Config(retries={"max_attempts": 1}),
        )
    return boto3.client(
        "sqs",
        endpoint_url=settings.aws_endpoint_url,
        region_name=settings.aws_region,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 1}),
    )


def handle_message(body: str) -> HealthcheckMessage:
    message = parse_healthcheck_message(body)
    logger.info("Healthcheck message handled request_id=%s", message.request_id)
    return message


def poll_once(client: object, queue_url: str) -> bool:
    response = client.receive_message(  # type: ignore[attr-defined]
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5,
        VisibilityTimeout=15,
    )
    messages = response.get("Messages", [])
    if not messages:
        return False
    message = messages[0]
    try:
        handle_message(message["Body"])
    except (KeyError, ValueError, json.JSONDecodeError):
        logger.exception("Invalid worker message left unacknowledged")
        return False
    client.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])  # type: ignore[attr-defined]
    return True
