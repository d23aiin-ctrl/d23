"""
Dependency Injection.

Wire up repositories and use cases for FastAPI.
"""

from functools import lru_cache

from domain.repositories import (
    HoroscopeRepository,
    KundliRepository,
    PanchangRepository
)
from infrastructure.repositories import (
    MockHoroscopeRepository,
    MockKundliRepository,
    MockPanchangRepository
)
from application.use_cases import (
    GetHoroscopeUseCase,
    GenerateKundliUseCase,
    MatchKundliUseCase,
    GetPanchangUseCase
)
from infrastructure.api.config import get_settings


# =============================================================================
# Repository Providers
# =============================================================================

@lru_cache()
def get_horoscope_repository() -> HoroscopeRepository:
    """Get horoscope repository instance."""
    settings = get_settings()
    if settings.USE_MOCK_DATA:
        return MockHoroscopeRepository()
    # Production: return HoroscopeRepositoryImpl(...)
    return MockHoroscopeRepository()


@lru_cache()
def get_kundli_repository() -> KundliRepository:
    """Get kundli repository instance."""
    settings = get_settings()
    if settings.USE_MOCK_DATA:
        return MockKundliRepository()
    # Production: return KundliRepositoryImpl(...)
    return MockKundliRepository()


@lru_cache()
def get_panchang_repository() -> PanchangRepository:
    """Get panchang repository instance."""
    settings = get_settings()
    if settings.USE_MOCK_DATA:
        return MockPanchangRepository()
    # Production: return PanchangRepositoryImpl(...)
    return MockPanchangRepository()


# =============================================================================
# Use Case Providers
# =============================================================================

def get_horoscope_use_case() -> GetHoroscopeUseCase:
    """Get horoscope use case."""
    return GetHoroscopeUseCase(
        horoscope_repository=get_horoscope_repository()
    )


def get_kundli_use_case() -> GenerateKundliUseCase:
    """Get kundli generation use case."""
    return GenerateKundliUseCase(
        kundli_repository=get_kundli_repository()
    )


def get_matching_use_case() -> MatchKundliUseCase:
    """Get kundli matching use case."""
    return MatchKundliUseCase(
        kundli_repository=get_kundli_repository()
    )


def get_panchang_use_case() -> GetPanchangUseCase:
    """Get panchang use case."""
    return GetPanchangUseCase(
        panchang_repository=get_panchang_repository()
    )
