"""Dependency injection for Vision Service."""

from functools import lru_cache

from infrastructure.api.config import Settings, get_settings
from infrastructure.external.dashscope_client import DashScopeClient
from infrastructure.external.ollama_client import OllamaClient
from infrastructure.repositories.dashscope_vision_repository import DashScopeVisionRepository
from infrastructure.repositories.ollama_vision_repository import OllamaVisionRepository
from application.use_cases.analyze_image import AnalyzeImageUseCase


@lru_cache()
def get_dashscope_client() -> DashScopeClient:
    settings = get_settings()
    return DashScopeClient(
        api_key=settings.DASHSCOPE_API_KEY,
        model=settings.DASHSCOPE_MODEL,
        base_url=settings.DASHSCOPE_BASE_URL,
        timeout=settings.REQUEST_TIMEOUT,
    )


@lru_cache()
def get_ollama_client() -> OllamaClient:
    settings = get_settings()
    return OllamaClient(
        server_url=settings.OLLAMA_SERVER,
        model=settings.OLLAMA_MODEL,
        vision_models=settings.OLLAMA_VISION_MODELS,
        timeout=settings.REQUEST_TIMEOUT,
    )


def get_dashscope_repository() -> DashScopeVisionRepository:
    return DashScopeVisionRepository(client=get_dashscope_client())


def get_ollama_repository() -> OllamaVisionRepository:
    return OllamaVisionRepository(client=get_ollama_client())


def get_analyze_use_case() -> AnalyzeImageUseCase:
    """Get the AnalyzeImageUseCase with DashScope as primary and Ollama as fallback."""
    settings = get_settings()

    # DashScope is primary if API key is available
    if settings.dashscope_available:
        primary = get_dashscope_repository()
        fallback = get_ollama_repository()
    else:
        # Ollama only mode
        primary = get_ollama_repository()
        fallback = None

    return AnalyzeImageUseCase(
        primary_repository=primary,
        fallback_repository=fallback,
    )
