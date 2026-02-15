"""
Application Configuration.

Centralized configuration using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Service info
    SERVICE_NAME: str = "travel-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8004

    # Feature flags
    USE_MOCK_DATA: bool = True  # Set to False for production

    # External APIs
    RAILWAY_API_URL: str = "https://api.railwayapi.com/v2"
    RAILWAY_API_KEY: str = ""

    # Cache
    CACHE_TTL_SECONDS: int = 300

    class Config:
        env_file = ".env"
        env_prefix = "TRAVEL_"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
