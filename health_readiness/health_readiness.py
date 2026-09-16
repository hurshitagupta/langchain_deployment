import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException


load_dotenv()


app = FastAPI(
    title="LangChain Health Service",
    version=os.getenv("APP_VERSION", "dev"),
)


def dependencies_ready() -> bool:
    """
    Check whether required external dependenciesare configured.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("MODEL_NAME")
    base_url = os.getenv("BASE_URL")

    return bool(api_key and model_name and base_url)


@app.get("/healthz")
def healthz():
    """
    Liveness probe.

    Confirms that the FastAPI application is running.
    """

    return {
        "status": "ok"
    }


@app.get("/readyz")
def readyz():
    """
    Readiness probe.

    Confirms that the required model configuration is available.
    """

    if not dependencies_ready():
        raise HTTPException(
            status_code=503,
            detail="service dependencies are not ready"
        )

    return {
        "status": "ready"
    }