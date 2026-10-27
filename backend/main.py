
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.nlp.chatbot import NLPChatbot


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the NLP model once when the API starts.
    app.state.chatbot = NLPChatbot()
    yield


app = FastAPI(
    title="NLP Chatbot API",
    description="An NLP chatbot powered by TF-IDF and Logistic Regression.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The message sent to the chatbot.",
    )


class ChatResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    method: str
    response: str


@app.get("/")
def root():
    return {
        "message": "Welcome to the NLP Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "NLP Chatbot API",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = app.state.chatbot.get_response(request.message)

    return ChatResponse(
        message=request.message,
        intent=result["intent"],
        confidence=result["confidence"],
        method=result["method"],
        response=result["response"],
    )
