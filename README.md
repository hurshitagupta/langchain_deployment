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

---

## Task 2 — Containerisation

Task 2 packages the FastAPI LangChain service into a Docker container so that the application can run in a consistent and reproducible environment.

### Implementation

The Dockerfile uses a Python 3.12 slim base image and installs the exact dependencies listed in the pinned `requirements.txt`.

The application is run using a dedicated `appuser` instead of the default root user. This reduces unnecessary privileges inside the container.

The `.dockerignore` file prevents local development files and secrets such as `.env` from being included in the Docker build context.

API credentials are not stored in the Docker image. They are supplied at runtime using environment variables.

### Build the Image

From the project root:

```bash
docker build -f containerisation/Dockerfile -t langchain-deployment:1.0 .
```

### Run the Container

```bash
docker run --rm -p 8000:8000 --env-file .env langchain-deployment:1.0
```

The container exposes the FastAPI service on port `8000`.

After starting the container, the local Swagger documentation can be accessed at:

```text
http://127.0.0.1:8000/docs
```

### Non-Root User

The Dockerfile creates and switches to a dedicated `appuser` before starting the application.

The running container user can be verified with:

```bash
docker exec <container_id> whoami
```

Expected output:

```text
appuser
```

### Reproducible Build

Python dependencies are pinned to exact versions in `requirements.txt`. This ensures that future Docker builds install the same dependency versions rather than automatically using newer releases.

### Secret Hygiene

The `.env` file is excluded through `.dockerignore` and is never copied into the Docker image.

Environment variables are provided when starting the container:

```bash
docker run --rm -p 8000:8000 --env-file .env langchain-deployment:1.0
```

### Automated Tests

Run the Task 2 tests with:

```bash
uv run pytest tests/test_containerisation.py -v
```

The tests verify the required Docker configuration, non-root execution configuration, and secret hygiene.

Save the test evidence with:

```bash
uv run pytest tests/test_containerisation.py -v > outputs/test_containerisation.txt 2>&1
```

The saved build log and automated test output provide evidence that the service can be packaged reproducibly and that the required container security configuration is present.

---

## Task 3 — Health and Readiness

Task 3 implements separate liveness and readiness probes for the deployed service.

### Implementation

Two HTTP endpoints are provided:

* `GET /healthz` — liveness probe that confirms the FastAPI application is running.
* `GET /readyz` — readiness probe that confirms the dependencies required by the LangChain service are configured.

The readiness check verifies that the required `OPENROUTER_API_KEY`, `MODEL_NAME`, and `BASE_URL` environment variables are available.

The liveness probe does not depend on external configuration. Therefore, the application can remain alive while reporting that it is not ready to serve model requests.

### Run Task 3

From the project root:

```bash
uv run uvicorn health_readiness.health_readiness:app --reload
```

The probes can then be accessed locally at:

```text
http://127.0.0.1:8000/healthz
http://127.0.0.1:8000/readyz
```

### Liveness

A healthy running application returns:

```json
{
  "status": "ok"
}
```

with HTTP status `200`.

### Readiness

When all required dependencies are configured, `/readyz` returns:

```json
{
  "status": "ready"
}
```

with HTTP status `200`.

If a required dependency such as `OPENROUTER_API_KEY` is unavailable, the readiness probe returns HTTP status `503`.

This separates application liveness from the application's ability to serve model requests.

### Automated Tests

The Task 3 automated tests verify:

* successful liveness response
* successful readiness response when dependencies are configured
* readiness failure when a required dependency is missing

Run the tests with:

```bash
uv run pytest tests/test_health_readiness.py -v
```

Save the test evidence with:

```bash
uv run pytest tests/test_health_readiness.py -v > outputs/test_health_readiness.txt 2>&1
```

Screenshots of successful liveness and readiness responses and the saved pytest output are included in the `outputs/` folder as supporting evidence.
