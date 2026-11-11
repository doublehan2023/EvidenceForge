FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/api:/app/worker

COPY pyproject.toml ./
COPY api ./api
COPY worker ./worker
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir '.[dev]'

EXPOSE 8000
CMD ["uvicorn", "evidenceforge_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
