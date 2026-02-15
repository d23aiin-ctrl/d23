"""
Travel Service - Clean Architecture.

This is the composition root where everything comes together.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from infrastructure.api.config import get_settings
from infrastructure.api.routers import pnr_router, train_router

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"Mock data: {settings.USE_MOCK_DATA}")
    yield
    logger.info("Shutting down")


# Create app
app = FastAPI(
    title="Travel Service (Clean Architecture)",
    description="Indian Railways travel service with proper architecture",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pnr_router)
app.include_router(train_router)


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "architecture": "Clean Architecture",
    }


@app.get("/")
async def root():
    """Service info."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "architecture": "Clean Architecture",
        "layers": {
            "domain": "Entities, Repository Interfaces",
            "application": "Use Cases, DTOs",
            "infrastructure": "API Routers, Repository Implementations",
        },
        "endpoints": {
            "pnr_status": "GET /pnr/{pnr_number}",
            "train_schedule": "GET /train/{train_number}/schedule",
            "train_status": "GET /train/{train_number}/status",
            "search_trains": "GET /trains/search?from=X&to=Y",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
