PYTHON ?= .venv/bin/python

.PHONY: up down logs migrate lint typecheck test smoke

up:
	docker compose up --build -d

down:
	docker compose down --volumes

logs:
	docker compose logs -f

migrate:
	docker compose run --rm api alembic upgrade head

lint:
	cd web && npm run lint
	$(PYTHON) -m ruff check api worker tests
	$(PYTHON) -m ruff format --check api worker tests

typecheck:
	cd web && npm run typecheck
	$(PYTHON) -m mypy api worker

test:
	cd web && npm test
	$(PYTHON) -m pytest

smoke:
	./scripts/smoke.sh
