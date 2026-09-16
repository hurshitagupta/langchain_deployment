from fastapi.testclient import TestClient

from http_api.http_api import app
import http_api.http_api as api_module


client = TestClient(app)


class FakeChain:
    async def ainvoke(self, data):
        return f"Test answer for: {data['question']}"

    async def astream(self, data):
        yield "Test "
        yield "stream "
        yield "response"


def test_invoke_success(monkeypatch):
    monkeypatch.setattr(
        api_module,
        "chain",
        FakeChain()
    )

    response = client.post("/v1/invoke",json={"question": "What is LangChain?"})

    assert response.status_code == 200
    assert response.json() == { "answer": "Test answer for: What is LangChain?"}


def test_invoke_invalid_input():
    response = client.post("/v1/invoke",json={"question": ""})

    assert response.status_code == 422


def test_stream_success(monkeypatch):
    monkeypatch.setattr(api_module,"chain",FakeChain())

    response = client.post("/v1/stream",json={"question": "Explain streaming"})

    assert response.status_code == 200
    assert response.text == "Test stream response"