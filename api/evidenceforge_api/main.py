from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from evidenceforge_api.config import get_settings
from evidenceforge_api.services.dependencies import check_dependencies


class DependencyHealthResponse(BaseModel):
    status: str
    dependencies: dict[str, str]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(title="EvidenceForge API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    """Process liveness probe without dependency access."""
    return {"status": "ok", "service": "api"}


@app.get("/api/v1/health/dependencies", response_model=DependencyHealthResponse)
async def dependency_health(response: Response) -> DependencyHealthResponse:
    result = await check_dependencies(get_settings())
    dependencies = {
        "database": "healthy" if result.database else "unhealthy",
        "object_storage": "healthy" if result.object_storage else "unhealthy",
        "queue": "healthy" if result.queue else "unhealthy",
    }
    if not result.healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return DependencyHealthResponse(
        status="healthy" if result.healthy else "unhealthy", dependencies=dependencies
    )
