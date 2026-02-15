"""AI Bot Service - FastAPI application with HTTP and WebSocket chat endpoints."""

import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot.conversation import ConversationManager
from bot.intent_classifier import IntentClassifier
from bot.response_formatter import ResponseFormatter
from bot.router import BotRouter
from clients.astrology_client import AstrologyClient
from clients.finance_client import FinanceClient
from clients.government_client import GovernmentClient
from clients.travel_client import TravelClient
from clients.utility_client import UtilityClient
from config import get_settings

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ai-bot-service")

# Global instances
bot_router: BotRouter | None = None
classifier: IntentClassifier | None = None
formatter: ResponseFormatter | None = None
conversation_mgr: ConversationManager | None = None


def _create_openai_client(settings):
    """Create OpenAI async client if API key is available."""
    if not settings.llm_available:
        logger.info("No OPENAI_API_KEY set - using rule-based mode (no LLM)")
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized - LLM mode enabled")
        return client
    except Exception as e:
        logger.warning("Failed to initialize OpenAI client: %s", e)
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    global bot_router, classifier, formatter, conversation_mgr

    settings = get_settings()
    openai_client = _create_openai_client(settings)

    # Initialize service clients
    travel = TravelClient(base_url=settings.TRAVEL_SERVICE_URL, timeout=settings.HTTP_TIMEOUT, max_retries=settings.HTTP_MAX_RETRIES)
    astrology = AstrologyClient(base_url=settings.ASTROLOGY_SERVICE_URL, timeout=settings.HTTP_TIMEOUT, max_retries=settings.HTTP_MAX_RETRIES)
    finance = FinanceClient(base_url=settings.FINANCE_SERVICE_URL, timeout=settings.HTTP_TIMEOUT, max_retries=settings.HTTP_MAX_RETRIES)
    government = GovernmentClient(base_url=settings.GOVERNMENT_SERVICE_URL, timeout=settings.HTTP_TIMEOUT, max_retries=settings.HTTP_MAX_RETRIES)
    utility = UtilityClient(base_url=settings.UTILITY_SERVICE_URL, timeout=settings.HTTP_TIMEOUT, max_retries=settings.HTTP_MAX_RETRIES)

    # Initialize core components
    bot_router = BotRouter(travel=travel, astrology=astrology, finance=finance, government=government, utility=utility)
    classifier = IntentClassifier(openai_client=openai_client, model=settings.OPENAI_MODEL)
    formatter = ResponseFormatter(openai_client=openai_client, model=settings.OPENAI_MODEL)
    conversation_mgr = ConversationManager(
        max_history=settings.MAX_HISTORY_LENGTH,
        session_timeout_minutes=settings.SESSION_TIMEOUT_MINUTES,
    )

    mode = "LLM" if openai_client else "Rule-Based"
    logger.info("AI Bot Service started on port %d [%s mode]", settings.PORT, mode)

    yield

    # Shutdown
    if bot_router:
        await bot_router.close()
    logger.info("AI Bot Service stopped")


# FastAPI app
app = FastAPI(
    title="AI Bot Service",
    version="1.0.0",
    description="AI-powered chatbot that routes queries to microservices",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# --- Request/Response models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    session_id: str
    entities: dict = {}
    needs_input: bool = False


# --- Endpoints ---

@app.get("/", response_class=FileResponse)
async def serve_ui():
    """Serve the web chat UI."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"message": "AI Bot Service is running. Chat UI not found."})


@app.post("/chat", response_model=ChatResponse)
async def chat_http(request: ChatRequest):
    """HTTP chat endpoint - send a message, get a response."""
    session_id = request.session_id or str(uuid.uuid4())
    result = await _process_message(request.message, session_id)
    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        confidence=result["confidence"],
        session_id=session_id,
        entities=result.get("entities", {}),
        needs_input=result.get("needs_input", False),
    )


@app.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """WebSocket chat endpoint for real-time messaging."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info("WebSocket connected: %s", session_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                message = payload.get("message", data)
                session_id = payload.get("session_id", session_id)
            except json.JSONDecodeError:
                message = data

            if not message.strip():
                continue

            # Send typing indicator
            await websocket.send_json({"type": "typing", "session_id": session_id})

            result = await _process_message(message, session_id)

            await websocket.send_json({
                "type": "message",
                "response": result["response"],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "session_id": session_id,
                "entities": result.get("entities", {}),
                "needs_input": result.get("needs_input", False),
            })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
    except Exception as e:
        logger.exception("WebSocket error for session %s", session_id)
        try:
            await websocket.send_json({"type": "error", "message": "An error occurred. Please try again."})
        except Exception:
            pass


@app.get("/health")
async def health_check():
    """Bot service health check."""
    settings = get_settings()
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy",
        "mode": "llm" if classifier and classifier.llm_available else "rule-based",
        "active_sessions": conversation_mgr.active_sessions_count() if conversation_mgr else 0,
    }


@app.get("/services/health")
async def services_health():
    """Check health of all downstream microservices."""
    if not bot_router:
        return {"status": "not_initialized"}

    results = {}
    for name, client in [
        ("travel", bot_router.travel),
        ("astrology", bot_router.astrology),
        ("finance", bot_router.finance),
        ("government", bot_router.government),
        ("utility", bot_router.utility),
    ]:
        results[name] = await client.health_check()

    all_healthy = all(r["status"] == "healthy" for r in results.values())
    return {
        "status": "all_healthy" if all_healthy else "degraded",
        "services": results,
    }


# --- Core processing ---

async def _process_message(message: str, session_id: str) -> dict:
    """Process a user message through the full pipeline."""
    # Store user message
    conversation_mgr.add_message(session_id, "user", message)

    # Step 1: Classify intent
    classification = await classifier.classify(message)
    logger.info(
        "Intent: %s (%.2f) | Entities: %s",
        classification.intent, classification.confidence, classification.entities,
    )

    # Step 2: Route to service
    route_result = await bot_router.route(classification)

    # Step 3: Format response
    raw_response = route_result.get("response", {})
    formatted = await formatter.format(
        intent=classification.intent,
        data=raw_response,
        user_message=message,
    )

    # Store assistant response
    conversation_mgr.add_message(
        session_id, "assistant", formatted,
        intent=classification.intent,
        metadata={"entities": classification.entities},
    )

    return {
        "response": formatted,
        "intent": classification.intent,
        "confidence": classification.confidence,
        "entities": classification.entities,
        "needs_input": route_result.get("needs_input", False),
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
