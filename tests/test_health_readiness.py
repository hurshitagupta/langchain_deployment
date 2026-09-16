from fastapi.testclient import TestClient

from health_readiness.health_readiness import app


client = TestClient(app)


def test_healthz_success():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == { "status": "ok" }


def test_readyz_success(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY","test-key")
    monkeypatch.setenv("MODEL_NAME","test-model")
    monkeypatch.setenv("BASE_URL","https://example.com")

    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readyz_failure_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY",raising=False)

    response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"detail": "service dependencies are not ready"}