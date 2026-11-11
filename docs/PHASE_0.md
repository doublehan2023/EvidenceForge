# Phase 0 foundation

The local development stack consists of a Next.js status page, FastAPI API,
Python worker, PostgreSQL with pgvector, and LocalStack emulating S3 and SQS.

Run `cp .env.example .env`, then `make up`, `make migrate`, and `make smoke`.
No authentication, research workflows, model calls, or production infrastructure
are implemented in this phase.
