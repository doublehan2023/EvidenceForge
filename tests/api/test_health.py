from fastapi.testclient import TestClient

from evidenceforge_api.main import app
from evidenceforge_api.services.dependencies import DependencyStatus


def test_process_health_does_not_check_dependencies() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api"}


async def test_dependency_health_reports_success(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def healthy(_: object) -> DependencyStatus:
        return DependencyStatus(database=True, object_storage=True, queue=True)

    monkeypatch.setattr("evidenceforge_api.main.check_dependencies", healthy)
    with TestClient(app) as client:
        response = client.get("/api/v1/health/dependencies")
    assert response.status_code == 200
    assert response.json()["dependencies"]["database"] == "healthy"


async def test_dependency_health_reports_failure(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def unhealthy(_: object) -> DependencyStatus:
        return DependencyStatus(database=False, object_storage=True, queue=False)

    monkeypatch.setattr("evidenceforge_api.main.check_dependencies", unhealthy)
    with TestClient(app) as client:
        response = client.get("/api/v1/health/dependencies")
    assert response.status_code == 503
    assert response.json()["dependencies"] == {
        "database": "unhealthy",
        "object_storage": "healthy",
        "queue": "unhealthy",
    }
