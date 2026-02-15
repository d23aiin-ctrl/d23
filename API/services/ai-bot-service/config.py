"""Configuration for AI Bot Service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "ai-bot-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 3002

    # OpenAI (optional - falls back to rule-based if not set)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Downstream service URLs
    TRAVEL_SERVICE_URL: str = "http://localhost:8004"
    ASTROLOGY_SERVICE_URL: str = "http://localhost:8003"
    FINANCE_SERVICE_URL: str = "http://localhost:8007"
    GOVERNMENT_SERVICE_URL: str = "http://localhost:8005"
    UTILITY_SERVICE_URL: str = "http://localhost:8006"
    VISION_SERVICE_URL: str = "http://localhost:8009"

    # Conversation settings
    MAX_HISTORY_LENGTH: int = 10
    SESSION_TIMEOUT_MINUTES: int = 30

    # HTTP client settings
    HTTP_TIMEOUT: float = 30.0
    HTTP_MAX_RETRIES: int = 2

    @property
    def llm_available(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    model_config = {"env_file": ".env", "env_prefix": "BOT_"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
