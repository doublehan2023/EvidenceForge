# EvidenceForge

EvidenceForge is a multi-tenant, evidence-grounded company-research agentic platform.
It will turn a company research request into a decision-ready memo whose
material claims are backed by preserved, auditable source evidence.

## Repository layout

```text
web/       Next.js application for the research workspace
api/       FastAPI HTTP API and domain-facing service layer
worker/    Asynchronous research-job execution service
infra/     Terraform infrastructure definitions
docs/      Architecture decisions and operating documentation
```

The services are intentionally separate. The web application serves users,
the API owns authenticated application access and persistent domain behavior,
and the worker will run long-lived research workflows independently of request
handling. `infra/` remains isolated so local application code does not depend
on cloud-provider resources.

## Phase 0 status

Phase 0 provides a one-command local development stack containing the web,
API, worker, PostgreSQL with pgvector, and LocalStack emulation for both
S3-compatible object storage and SQS.

## Local configuration

Copy `.env.example` to `.env` before running the future local stack:

```sh
cp .env.example .env
```

`.env` is intentionally untracked. Do not commit credentials or environment-
specific endpoints.

## Quick start

Install local development dependencies once:

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
(cd web && npm ci)
```

Then start and verify the local platform:

```sh
make up
make migrate
make smoke
```

Open `http://localhost:3000` to see the frontend status page. Run `make lint`,
`make typecheck`, and `make test` before opening a pull request.

## Development principles

- Persist evidence, claims, citations, and agent execution records as durable
  domain data rather than ephemeral chat state.
- Keep workspace scoping explicit at every data-access boundary.
- Design local dependencies to match production contracts where practical.
- Add migrations, tests, formatting, type checks, and CI alongside each new
  service rather than deferring them.
