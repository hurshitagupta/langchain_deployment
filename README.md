# LangChain Deployment

This project implements the LangChain Deployment hands-on assessment. The assessment focuses on exposing a LangChain application as an HTTP service and gradually adding deployment features such as containerisation, health checks, limits, and rollout handling.

## Task 1 — HTTP API

Task 1 exposes the LangChain chain through a FastAPI HTTP service.

### Implementation

The API provides two endpoints:

* `POST /v1/invoke` — invokes the LangChain chain and returns the complete model response.
* `POST /v1/stream` — streams the model response as it is generated.

A Pydantic `AskRequest` schema validates incoming requests. The `question` field must contain between 1 and 2000 characters. Invalid requests are rejected automatically by FastAPI before reaching the model.

The application uses environment variables for model configuration and API credentials. No API keys are stored directly in the source code.

### Run the API

From the project root:

```bash
uv run uvicorn http_api.http_api:app --reload
```

The API runs locally on port `8000`.

FastAPI Swagger documentation is available at `/docs`.

### Streaming

The `/v1/stream` endpoint uses LangChain's asynchronous `astream()` method and FastAPI's `StreamingResponse` to return the generated answer progressively.

### Automated Tests

Task 1 includes automated tests. Run the tests with:

```bash
uv run pytest tests/test_http_api.py -v
```

### Evidence

Test output can be saved using:

```bash
uv run pytest tests/test_http_api.py -v > outputs/test_http_api.txt 2>&1
```

The saved output provides evidence that the HTTP API success, validation failure, and streaming cases work correctly.

`Screenshots and automated test outputs are included in the outputs/ folder as evidence of the API behaviour.`