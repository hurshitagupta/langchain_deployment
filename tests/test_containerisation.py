from pathlib import Path


DOCKERFILE = Path("containerisation/Dockerfile")


def test_dockerfile_has_required_configuration():
    content = DOCKERFILE.read_text()

    assert "FROM python:3.12-slim" in content
    assert "WORKDIR /app" in content
    assert "requirements.txt" in content
    assert "USER appuser" in content
    assert "EXPOSE 8000" in content
    assert "uvicorn" in content


def test_dockerfile_does_not_copy_env_file():
    content = DOCKERFILE.read_text()

    assert "COPY .env" not in content
    assert "ADD .env" not in content


def test_dockerignore_protects_env_file():
    dockerignore = Path(".dockerignore").read_text()

    assert ".env" in dockerignore