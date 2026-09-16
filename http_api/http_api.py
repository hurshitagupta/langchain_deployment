import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter


load_dotenv()


model = ChatOpenRouter(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

prompt = ChatPromptTemplate.from_template(
    "Answer briefly in 20 words and clearly: {question}"
)

chain = prompt | model | StrOutputParser()

app = FastAPI(
    title="LangChain Deployment Service",
    version=os.getenv("APP_VERSION", "dev"),
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.post("/v1/invoke")
async def invoke(body: AskRequest):
    answer = await chain.ainvoke(
        {"question": body.question}
    )

    return {
        "answer": answer
    }


@app.post("/v1/stream")
async def stream(body: AskRequest):

    async def generate():
        async for chunk in chain.astream({"question": body.question}):
            yield chunk

    return StreamingResponse(generate(),media_type="text/plain")