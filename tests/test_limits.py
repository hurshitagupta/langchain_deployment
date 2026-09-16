import asyncio

from fastapi.testclient import TestClient

import limits.limits as limits_module
from limits.limits import app


client = TestClient(app)


class FakeChain:
    async def ainvoke(self, data):
        return "Test answer"


class SlowChain:
    async def ainvoke(self, data):
        await asyncio.sleep(0.2)
        return "Slow answer"


def setup_function():
    limits_module.request_history.clear()


def test_normal_request(monkeypatch):
    monkeypatch.setattr(limits_module,"chain",FakeChain())

    response = client.post( "/v1/invoke", json={"question": "What is LangChain?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Test answer"}


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(limits_module,"chain", FakeChain())

    for _ in range(5):
        response = client.post("/v1/invoke",json={"question": "Test"})

        assert response.status_code == 200

    response = client.post("/v1/invoke",json={"question": "Test"})

    assert response.status_code == 429


def test_request_size_limit():
    response = client.post( "/v1/invoke", json={"question": "a" * 5000})

    assert response.status_code == 413


def test_timeout(monkeypatch):
    monkeypatch.setattr(limits_module,"chain", SlowChain())

    monkeypatch.setattr(limits_module, "REQUEST_TIMEOUT", 0.05)

    response = client.post("/v1/invoke",json={"question": "Test timeout"})

    assert response.status_code == 504