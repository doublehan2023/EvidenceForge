"""Test-only process configuration set before application modules are imported."""

import os

_TEST_ENVIRONMENT = {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/evidenceforge_test",
    "S3_BUCKET": "evidenceforge-test",
    "SQS_QUEUE_NAME": "research-runs-test",
    "AWS_ENDPOINT_URL": "http://localhost:4566",
    "CORS_ALLOWED_ORIGINS": "http://localhost:3000",
}

for _name, _value in _TEST_ENVIRONMENT.items():
    os.environ.setdefault(_name, _value)
