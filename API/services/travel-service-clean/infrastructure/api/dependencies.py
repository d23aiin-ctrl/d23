"""
Dependency Injection.

This is where we wire everything together.
FastAPI's Depends() system handles DI.
"""

from functools import lru_cache
from typing import Generator

from application.use_cases import (
    GetPNRStatusUseCase,
    GetTrainScheduleUseCase,
    SearchTrainsUseCase,
    GetLiveStatusUseCase,
)
from domain.repositories import PNRRepository, TrainRepository
from infrastructure.repositories import (
    MockPNRRepository,
    MockTrainRepository,
    PNRRepositoryImpl,
    TrainRepositoryImpl,
)
from infrastructure.api.config import get_settings


# ============================================================================
# Repository Providers
# ============================================================================

@lru_cache()
def get_pnr_repository() -> PNRRepository:
    """
    Get PNR repository instance.

    In production, returns real API implementation.
    In development/testing, returns mock.
    """
    settings = get_settings()

    if settings.USE_MOCK_DATA:
        return MockPNRRepository()

    return PNRRepositoryImpl(
        api_url=settings.RAILWAY_API_URL,
        api_key=settings.RAILWAY_API_KEY,
    )


@lru_cache()
def get_train_repository() -> TrainRepository:
    """
    Get Train repository instance.
    """
    settings = get_settings()

    if settings.USE_MOCK_DATA:
        return MockTrainRepository()

    return TrainRepositoryImpl(
        api_url=settings.RAILWAY_API_URL,
        api_key=settings.RAILWAY_API_KEY,
    )


# ============================================================================
# Use Case Providers
# ============================================================================

def get_pnr_use_case() -> GetPNRStatusUseCase:
    """Get PNR status use case with injected repository."""
    return GetPNRStatusUseCase(
        pnr_repository=get_pnr_repository()
    )


def get_schedule_use_case() -> GetTrainScheduleUseCase:
    """Get train schedule use case."""
    return GetTrainScheduleUseCase(
        train_repository=get_train_repository()
    )


def get_search_use_case() -> SearchTrainsUseCase:
    """Get train search use case."""
    return SearchTrainsUseCase(
        train_repository=get_train_repository()
    )


def get_live_status_use_case() -> GetLiveStatusUseCase:
    """Get live status use case."""
    return GetLiveStatusUseCase(
        train_repository=get_train_repository()
    )
