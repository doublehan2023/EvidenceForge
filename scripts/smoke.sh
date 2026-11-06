#!/bin/sh
set -eu

docker compose up -d
if [ "${CI:-}" = "true" ]; then
  trap 'docker compose down --volumes' EXIT
fi

for attempt in $(seq 1 30); do
  if curl -fsS http://localhost:8000/health >/dev/null; then break; fi
  [ "$attempt" -eq 30 ] && exit 1
  sleep 2
done

docker compose run --rm api alembic upgrade head
curl -fsS http://localhost:8000/api/v1/health/dependencies
curl -fsS http://localhost:3000 >/dev/null

request_id="$(python3 -c 'import uuid; print(uuid.uuid4())')"
sent_at="$(python3 -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"
payload="{\"type\":\"healthcheck\",\"request_id\":\"${request_id}\",\"sent_at\":\"${sent_at}\"}"
docker compose exec -T localstack awslocal sqs send-message --queue-url http://localstack:4566/000000000000/research-runs --message-body "$payload" >/dev/null

for attempt in $(seq 1 15); do
  if docker compose logs worker | grep -q "request_id=${request_id}"; then exit 0; fi
  sleep 1
done
exit 1
