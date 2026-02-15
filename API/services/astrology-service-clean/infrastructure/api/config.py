"""
Service Configuration.

Environment-based settings using pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Service info
    SERVICE_NAME: str = "astrology-service"
    SERVICE_VERSION: str = "1.0.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8003

    # Environment
    DEBUG: bool = True
    USE_MOCK_DATA: bool = True

    # External APIs (for production)
    ASTROLOGY_API_URL: str = ""
    ASTROLOGY_API_KEY: str = ""

    # Cache settings
    REDIS_URL: str = ""
    CACHE_TTL_SECONDS: int = 3600

    # CORS
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
