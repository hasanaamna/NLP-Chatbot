
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel, Field

from src.nlp.ai_assistant import AIAssistant


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.assistant = AIAssistant()
    yield


app = FastAPI(
    title="AI Assistant API",
    description="A conversational AI assistant powered by Groq.",
    version="2.0.0",
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
        max_length=8000,
        description="The message sent to the AI assistant.",
    )
    conversation_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Optional ID used to continue a conversation.",
    )


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    response: str
    intent: str = "assistant"
    confidence: float = 0.0
    method: str = "groq_api"
    model: str


@app.get("/")
def root():
    return {
        "message": "Welcome to the AI Assistant API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Assistant API",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = app.state.assistant.get_response(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return ChatResponse(
            message=request.message,
            conversation_id=result["conversation_id"],
            response=result["response"],
            intent="assistant",
            confidence=0.0,
            method="groq_api",
            model=result["model"],
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except RuntimeError as exc:
        # Missing configuration or an unusable provider response.
        message = str(exc)
        status_code = 503 if "GROQ_API_KEY" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from exc

    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="The AI service is rate-limited. Please try again shortly.",
        ) from exc

    except APIConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the AI service. Please try again.",
        ) from exc

    except APIStatusError as exc:
        logger.warning("Groq API returned status %s", exc.status_code)
        raise HTTPException(
            status_code=502,
            detail="The AI service could not complete your request.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error while generating an AI response")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the response.",
        ) from exc
