from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from answer import answer_question


app = FastAPI(title="ProductRAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []


class ContextChunk(BaseModel):
    page_content: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    context: list[ContextChunk]


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer_text, chunks = answer_question(req.question, req.history)
    return ChatResponse(
        answer=answer_text,
        context=[
            ContextChunk(page_content=c.page_content, metadata=c.metadata)
            for c in chunks
        ],
    )
