"""Vision Service - Image analysis with Qwen VL (DashScope) and Ollama fallback."""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.config import get_settings
from infrastructure.api.routers import vision_router
from infrastructure.api.dependencies import (
    get_dashscope_client,
    get_ollama_client,
    get_analyze_use_case,
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("vision-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    settings = get_settings()

    # Check backend availability at startup
    use_case = get_analyze_use_case()
    availability = await use_case.check_availability()

    backends = []
    if settings.dashscope_available:
        backends.append("DashScope (qwen-vl-plus)")
    if availability.get("fallback_available"):
        backends.append("Ollama (local)")
    elif not settings.dashscope_available:
        backends.append("Ollama (local)")

    if not availability.get("any_available"):
        logger.warning("No vision backend available! Service will return errors.")
    else:
        logger.info("Vision backends available: %s", ", ".join(backends))

    logger.info("Vision Service started on port %d", settings.PORT)

    yield

    # Cleanup
    dashscope = get_dashscope_client()
    ollama = get_ollama_client()
    await dashscope.close()
    await ollama.close()
    logger.info("Vision Service stopped")


# FastAPI app
app = FastAPI(
    title="Vision Service",
    version="1.0.0",
    description="Image analysis service with OCR, object detection, document analysis, and more",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vision_router, tags=["Vision"])


@app.get("/")
async def root():
    settings = get_settings()
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "endpoints": [
            "POST /describe - Describe image contents",
            "POST /extract-text - OCR / text extraction",
            "POST /detect-objects - Object detection",
            "POST /analyze-document - Document analysis",
            "POST /analyze-receipt - Receipt/bill parsing",
            "POST /identify-food - Food identification",
            "POST /query - Custom image query",
            "GET /availability - Check backend availability",
            "GET /health - Health check",
        ],
    }


@app.get("/health")
async def health_check():
    settings = get_settings()
    use_case = get_analyze_use_case()
    availability = await use_case.check_availability()

    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy" if availability.get("any_available") else "degraded",
        "backends": {
            "dashscope": "available" if availability.get("primary_available") and settings.dashscope_available else "unavailable",
            "ollama": "available" if availability.get("fallback_available") or (not settings.dashscope_available and availability.get("primary_available")) else "unavailable",
        },
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
