"""
Astrology Service - Main Entry Point.

Clean Architecture implementation for astrology APIs.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.config import get_settings
from infrastructure.api.routers import (
    horoscope_router,
    kundli_router,
    panchang_router
)

settings = get_settings()

app = FastAPI(
    title="Astrology Service",
    description="""
    Astrology API with Clean Architecture.

    Features:
    - **Horoscope**: Daily/Weekly/Monthly predictions for all zodiac signs
    - **Kundli**: Birth chart generation with planet positions
    - **Matching**: Kundli matching for marriage compatibility (Guna Milan)
    - **Panchang**: Hindu calendar with Tithi, Nakshatra, Yoga, Karana

    Supports both English and Hindi inputs/outputs.
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(horoscope_router)
app.include_router(kundli_router)
app.include_router(panchang_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service info."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "docs": "/docs",
        "endpoints": {
            "horoscope": "/horoscope",
            "kundli": "/kundli",
            "matching": "/kundli/match",
            "panchang": "/panchang"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
