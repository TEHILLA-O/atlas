from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from atlas.apps.api.main import create_app
from atlas.config.settings import Settings


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(env="test", model_provider="demo"))
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_openapi(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    docs = client.get("/openapi.json")
    assert docs.status_code == 200
    paths = docs.json()["paths"]
    assert "/research" in paths
    assert "/documents" in paths
    assert "/research/{research_id}/events" in paths
