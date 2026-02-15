"""Configuration for Vision Service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "vision-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8009

    # DashScope API (Alibaba Qwen VL) - Primary
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_MODEL: str = "qwen-vl-plus"
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

    # Ollama (Local LLM) - Fallback
    OLLAMA_SERVER: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3-vl:8b"
    OLLAMA_VISION_MODELS: list[str] = ["qwen2.5vl:7b", "qwen3-vl:8b", "moondream:latest", "llava"]

    # Image processing
    MAX_IMAGE_SIZE: int = 1024
    SUPPORTED_FORMATS: str = "jpg,jpeg,png,webp,gif"

    # Timeouts
    REQUEST_TIMEOUT: float = 120.0

    @property
    def dashscope_available(self) -> bool:
        return bool(self.DASHSCOPE_API_KEY)

    @property
    def supported_formats_list(self) -> list[str]:
        return [f.strip().lower() for f in self.SUPPORTED_FORMATS.split(",")]

    model_config = {"env_file": ".env", "env_prefix": "VISION_"}


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
