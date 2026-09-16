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

---

## Task 4 — Limits

Task 4 adds basic request limits to the deployed LangChain API. The goal is to prevent excessive requests, oversized inputs, and model calls that take too long.

### Implemented Limits

The API implements three limits:

| Limit              |          Configured Value | Failure Response |
| ------------------ | ------------------------: | ---------------: |
| Per-IP rate limit  | 5 requests per 60 seconds |         HTTP 429 |
| Request size limit |                4096 bytes |         HTTP 413 |
| Request timeout    |                10 seconds |         HTTP 504 |

### 1. Per-IP Rate Limiting

The API tracks recent request timestamps for each client IP.

Only requests made during the last 60 seconds are counted. A client can make up to 5 requests within this window.

If the limit is exceeded, the API returns:

```text
HTTP 429
rate limit exceeded
```

Old request timestamps are removed once they fall outside the 60-second window.

### 2. Request Size Limit

Before sending the question to the LangChain model, the application calculates the size of the question in bytes.

The maximum allowed size is:

```text
4096 bytes
```

If the request exceeds this limit, the API returns:

```text
HTTP 413
request too large
```

### 3. Per-Request Timeout

The LangChain model call is executed using `asyncio.wait_for()`.

The configured timeout is:

```text
10 seconds
```

If the model does not respond within this time, the request is stopped and the API returns:

```text
HTTP 504
request timed out
```

This prevents a slow or unresponsive model request from waiting indefinitely.

### Run the Application

From the project root:

```bash
uv run uvicorn limits.limits:app --reload
```

The FastAPI Swagger interface is available at:

```text
http://127.0.0.1:8000/docs
```

Use the `POST /v1/invoke` endpoint to send a question.

Example request:

```json
{
  "question": "What is LangChain?"
}
```

A successful request returns HTTP `200` with the model response.

### Automated Tests

The automated tests cover both successful and failure scenarios without requiring unnecessary external model calls.

```bash
uv run pytest tests/test_limits.py -v
```

Save the test output as evidence:

```bash
uv run pytest tests/test_limits.py -v > outputs/test_limits.txt 2>&1
```

---

## Task 5 — Rollout and Rollback

Task 5 demonstrates a simple rollout and rollback process using a local version-based simulation.

The goal is to show what happens when a new release fails its readiness check and how the application can return to the previous stable version.

### Implementation

The rollout simulation is implemented in:

```text
rollout/rollout.py
```

Two versions are used in the simulation:

* `1.0.0` — previous stable version
* `1.1.0` — new release

The `deploy()` function simulates deploying a version and checking whether it is ready.

If the readiness check succeeds, the deployment is marked as successful.

If the readiness check fails, the deployment returns a failure result and the `rollback()` function restores the previous stable version.


### Run the Rollout Simulation

Run:

```bash
uv run python -m rollout.rollout
```

### Bad Release Evidence

The bad release output is saved as evidence using:

```bash
uv run python -m rollout.rollout > outputs/rollout.txt 2>&1
```

This output demonstrates that version `1.1.0` failed its simulated readiness check and triggered a rollback to version `1.0.0`.

### Automated Tests

Run:

```bash
uv run pytest tests/test_rollout.py -v
```

Save the test output:

```bash
uv run pytest tests/test_rollout.py -v > outputs/test_rollout.txt 2>&1
```

---

## Guardrails and Evidence

The project includes shared guardrails to prevent uncontrolled execution and oversized inputs during the assessment.

The main guardrail logic is stored in:

```text
guardrails.py
```

Evidence for the implemented guardrails is generated using:

```text
guardrails_evidence.py
```

This evidence file intentionally triggers the guardrails so their behaviour can be demonstrated and saved as part of the 

### Shared Guardrail Design

The guardrails are kept in a shared module rather than rewriting the same checks separately for every task.

The implemented guardrail evidence demonstrates:

* Hard step limit
* Per-operation timeout
* Capped retry attempts
* Input/token budget enforcement

### Run Guardrail Evidence

```bash
uv run python guardrails_evidence.py
```

### Save Guardrail Evidence

```bash
uv run python guardrails_evidence.py > outputs/guardrails_evidence_output.txt
```

The saved output provides reproducible evidence that each guardrail fires when its configured limit or failure condition is reached.

---

## Environment Configuration

The project uses environment variables to keep API credentials and model configuration outside the source code.

An `.env.example` file is included to show the required environment variables without exposing any actual secrets:

Create a local `.env` file using the same variables and provide your own values.

The actual `.env` file is excluded from GitHub using `.gitignore` to ensure that API keys are not committed to the repository.

## Requirements

The `requirements.txt` file contains the Python dependencies required to run the assessment.

Install the dependencies using:

```bash
uv pip install -r requirements.txt
```

The main dependencies used in this assessment include LangChain, OpenRouter integration, FastAPI, Uvicorn, python-dotenv, HTTPX, and pytest.

After installing the dependencies and configuring the `.env` file, the individual assessment tasks can be executed using the commands provided in their respective sections above.