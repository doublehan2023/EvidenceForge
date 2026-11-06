import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from evidenceforge_worker.queue import parse_healthcheck_message, poll_once


class FakeClient:
    def __init__(self, message: dict[str, str] | None) -> None:
        self.message = message
        self.deleted = False

    def receive_message(self, **_: object) -> dict[str, list[dict[str, str]]]:
        return {"Messages": [self.message]} if self.message else {}

    def delete_message(self, **_: object) -> None:
        self.deleted = True


def valid_body() -> str:
    return json.dumps(
        {
            "type": "healthcheck",
            "request_id": str(uuid4()),
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
    )


def test_parses_healthcheck() -> None:
    assert parse_healthcheck_message(valid_body()).request_id


def test_rejects_unknown_message_type() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        parse_healthcheck_message('{"type":"research"}')


def test_invalid_json_is_not_acknowledged() -> None:
    client = FakeClient({"Body": "not-json", "ReceiptHandle": "receipt"})
    assert poll_once(client, "queue-url") is False
    assert client.deleted is False


def test_valid_message_is_acknowledged() -> None:
    client = FakeClient({"Body": valid_body(), "ReceiptHandle": "receipt"})
    assert poll_once(client, "queue-url") is True
    assert client.deleted is True
