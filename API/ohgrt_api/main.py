"""
OhGrt API - FastAPI Application Entry Point.

This is the main entry point for the OhGrt API application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
import uvicorn

from ohgrt_api.config import settings
from ohgrt_api.auth import router as auth_router
from ohgrt_api.chat import router as chat_router
from ohgrt_api.admin.router import router as admin_router
from ohgrt_api.web import web_router
from whatsapp_bot.webhook.handler import router as whatsapp_webhook_router
from ohgrt_api.oauth import gmail_router, github_router, slack_router, jira_router, uber_router
from ohgrt_api.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    MetricsMiddleware,
)
from ohgrt_api.middleware.metrics import metrics
from common.whatsapp.client import initialize_whatsapp_client

logger = logging.getLogger(__name__)
_STANDARD_METHODS = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"}
_LOG_HEADERS = {
    "user-agent",
    "host",
    "x-forwarded-for",
    "x-real-ip",
    "forwarded",
    "via",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting OhGrt API services...")

    # Store settings in app state
    app.state.settings = settings

    # Initialize WhatsApp client if configured
    if settings.whatsapp_access_token and settings.whatsapp_phone_number_id:
        initialize_whatsapp_client(
            access_token=settings.whatsapp_access_token,
            phone_number_id=settings.whatsapp_phone_number_id,
        )
        logger.info("WhatsApp client initialized")

    # Configure LangSmith
    settings.configure_langsmith()

    logger.info(f"OhGrt API v{settings.api_version} started")

    yield

    # Shutdown
    logger.info("Shutting down OhGrt API services...")


app = FastAPI(
    lifespan=lifespan,
    title=settings.api_name,
    description="""
# OhGrt Agentic AI API

An intelligent AI assistant API with tool-use capabilities and multi-provider integrations.

## Features

- **Google Authentication**: Sign in with Google via Firebase
- **AI Chat**: Intelligent chat with tool-use capabilities
- **Provider Integrations**: Connect GitHub, Jira, Slack, and more
- **RAG Support**: Upload and query PDF documents
- **Weather Queries**: Get real-time weather information
    """,
    version=settings.api_version,
    contact={
        "name": "OhGrt Support",
        "email": "support@ohgrt.com",
    },
)


# Exception handlers
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.exception(
        "unhandled_exception %s %s (%s)",
        request.method,
        request.url.path,
        type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred.",
        },
    )


@app.middleware("http")
async def log_unusual_requests(request: Request, call_next):
    response = await call_next(request)
    method = request.method.upper()
    if method not in _STANDARD_METHODS or response.status_code == 405:
        client_ip = request.client.host if request.client else "-"
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() in _LOG_HEADERS
        }
        logger.warning(
            "unusual_request method=%s path=%s status=%s client=%s headers=%s query=%s",
            method,
            request.url.path,
            response.status_code,
            client_ip,
            headers,
            request.url.query or "-",
        )
    return response


# Middleware (order: last added = first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(web_router)
app.include_router(whatsapp_webhook_router)

# OAuth provider routers
app.include_router(gmail_router, prefix="/auth/providers/gmail", tags=["oauth-gmail"])
app.include_router(github_router, prefix="/auth/providers/github", tags=["oauth-github"])
app.include_router(slack_router, prefix="/auth/providers/slack", tags=["oauth-slack"])
app.include_router(jira_router, prefix="/auth/providers/jira", tags=["oauth-jira"])
app.include_router(uber_router, prefix="/auth/providers/uber", tags=["oauth-uber"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.api_name,
        "version": settings.api_version,
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": settings.api_version}


@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    # Could add database connectivity check here
    return {"status": "ready"}


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(
        content=metrics.export_prometheus(),
        media_type="text/plain; charset=utf-8",
    )


@app.get("/upstox/callback")
async def upstox_callback(request: Request):
    """Upstox OAuth callback - redirects to iOS app."""
    query_string = str(request.query_params)
    return RedirectResponse(
        url=f"niftyoptioncalculator://callback?{query_string}",
        status_code=302
    )


if __name__ == "__main__":
    uvicorn.run("ohgrt_api.main:app", host="0.0.0.0", port=9002, reload=True)
