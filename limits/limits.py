import asyncio
import os
import time
from collections import defaultdict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter


load_dotenv()


# Limits
RATE_LIMIT = 5
RATE_WINDOW = 60
MAX_REQUEST_SIZE = 4096
REQUEST_TIMEOUT = 10

request_history = defaultdict(list)


model = ChatOpenRouter(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


prompt = ChatPromptTemplate.from_template("Answer briefly and clearly: {question}")

chain = prompt | model | StrOutputParser()

app = FastAPI(title="LangChain Service with Limits")

class AskRequest(BaseModel):
    question: str = Field(min_length=1,max_length=10000)


@app.post("/v1/invoke")
async def invoke(body: AskRequest, request: Request):

    request_size = len( body.question.encode("utf-8"))

    if request_size > MAX_REQUEST_SIZE:
        raise HTTPException(
            status_code=413,
            detail="request too large"
        )


    client_ip = (request.client.host if request.client else "unknown")

    current_time = time.time()

    recent_requests = [timestamp for timestamp in request_history[client_ip]
        if current_time - timestamp < RATE_WINDOW
    ]

    request_history[client_ip] = recent_requests

    if len(recent_requests) >= RATE_LIMIT:
        raise HTTPException(status_code=429,detail="rate limit exceeded")

    request_history[client_ip].append(current_time)

    try:
        answer = await asyncio.wait_for(chain.ainvoke({"question": body.question}),timeout=REQUEST_TIMEOUT)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="request timed out")

    return {
        "answer": answer
    }