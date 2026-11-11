FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/api:/app/worker

COPY pyproject.toml ./
COPY api ./api
COPY worker ./worker
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

CMD ["python", "-m", "evidenceforge_worker.main"]
