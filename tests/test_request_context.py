from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_includes_request_id():
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_health_request_ids_are_unique():
    first = client.get("/health").headers["X-Request-ID"]
    second = client.get("/health").headers["X-Request-ID"]
    assert first != second
