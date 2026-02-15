"""Service Configuration."""
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "government-service"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8005
    DEBUG: bool = True
    USE_MOCK_DATA: bool = True
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
