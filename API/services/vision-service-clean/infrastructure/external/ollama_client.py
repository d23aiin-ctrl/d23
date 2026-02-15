"""Ollama client for local vision LLM inference."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local Ollama server with vision models."""

    def __init__(
        self,
        server_url: str = "http://localhost:11434",
        model: str = "qwen3-vl:8b",
        vision_models: list[str] | None = None,
        timeout: float = 120.0,
    ):
        self.server_url = server_url.rstrip("/")
        self.model = model
        self.vision_models = vision_models or ["qwen2.5vl:7b", "qwen3-vl:8b", "moondream:latest", "llava"]
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._available_model: str | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def is_available(self) -> bool:
        """Check if Ollama server is available with a vision model."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.server_url}/api/tags", timeout=5.0)
            if response.status_code != 200:
                return False

            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]

            # Check if any vision model is available
            for vision_model in self.vision_models:
                for available_model in models:
                    if vision_model.split(":")[0] in available_model:
                        self._available_model = available_model
                        logger.info("Found Ollama vision model: %s", available_model)
                        return True

            # Check if configured model is available
            for available_model in models:
                if self.model.split(":")[0] in available_model:
                    self._available_model = available_model
                    return True

            logger.warning("No vision model found in Ollama. Available: %s", models)
            return False

        except Exception as e:
            logger.debug("Ollama availability check failed: %s", e)
            return False

    async def get_model(self) -> str:
        """Get the best available vision model."""
        if self._available_model:
            return self._available_model
        await self.is_available()
        return self._available_model or self.model

    async def analyze(self, image_base64: str, prompt: str) -> dict[str, Any]:
        """Send an image with a prompt to Ollama for analysis."""
        client = await self._get_client()
        model = await self.get_model()

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
        }

        try:
            response = await client.post(f"{self.server_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            text = data.get("response", "")
            return {"success": bool(text), "text": text, "raw": data, "model": model}

        except httpx.HTTPStatusError as e:
            logger.error("Ollama API error: %s", e)
            return {"success": False, "text": "", "error": f"API error: {e.response.status_code}"}
        except Exception as e:
            logger.exception("Ollama request failed")
            return {"success": False, "text": "", "error": str(e)}

    async def chat(self, image_base64: str, messages: list[dict]) -> dict[str, Any]:
        """Send a chat request with an image to Ollama."""
        client = await self._get_client()
        model = await self.get_model()

        # Add image to the last user message
        chat_messages = []
        for msg in messages:
            if msg.get("role") == "user" and image_base64:
                chat_messages.append({
                    "role": "user",
                    "content": msg.get("content", ""),
                    "images": [image_base64],
                })
            else:
                chat_messages.append(msg)

        payload = {
            "model": model,
            "messages": chat_messages,
            "stream": False,
        }

        try:
            response = await client.post(f"{self.server_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            message = data.get("message", {})
            text = message.get("content", "")
            return {"success": bool(text), "text": text, "raw": data, "model": model}

        except httpx.HTTPStatusError as e:
            logger.error("Ollama chat error: %s", e)
            return {"success": False, "text": "", "error": f"API error: {e.response.status_code}"}
        except Exception as e:
            logger.exception("Ollama chat failed")
            return {"success": False, "text": "", "error": str(e)}
