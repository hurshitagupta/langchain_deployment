FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY http_api ./http_api

RUN useradd --create-home appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "http_api.http_api:app", "--host", "0.0.0.0", "--port", "8000"]