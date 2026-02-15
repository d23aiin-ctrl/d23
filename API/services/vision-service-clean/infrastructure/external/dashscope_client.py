"""DashScope API client for Alibaba Qwen VL vision model."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DashScopeClient:
    """Client for DashScope (Alibaba Qwen VL) API."""

    def __init__(
        self,
        api_key: str,
        model: str = "qwen-vl-plus",
        base_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def is_available(self) -> bool:
        """Check if DashScope API is available."""
        if not self.api_key:
            return False
        try:
            # Simple check - try to access the API
            client = await self._get_client()
            # DashScope doesn't have a simple health endpoint, so we just check connectivity
            response = await client.get(
                "https://dashscope.aliyuncs.com/api/v1/services",
                timeout=5.0,
            )
            return response.status_code in (200, 401, 403)  # Any response means API is reachable
        except Exception as e:
            logger.debug("DashScope availability check failed: %s", e)
            return False

    async def analyze(self, image_base64: str, prompt: str) -> dict[str, Any]:
        """Send an image with a prompt to Qwen VL for analysis."""
        client = await self._get_client()

        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/jpeg;base64,{image_base64}"},
                            {"text": prompt},
                        ],
                    }
                ]
            },
            "parameters": {},
        }

        try:
            response = await client.post(self.base_url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract the response text
            output = data.get("output", {})
            choices = output.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", [])
                if content and isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            return {"success": True, "text": item["text"], "raw": data}
                        elif isinstance(item, str):
                            return {"success": True, "text": item, "raw": data}

            # Fallback: try to get text from output directly
            text = output.get("text", "")
            if text:
                return {"success": True, "text": text, "raw": data}

            return {"success": False, "text": "", "error": "No response text found", "raw": data}

        except httpx.HTTPStatusError as e:
            logger.error("DashScope API error: %s", e)
            return {"success": False, "text": "", "error": f"API error: {e.response.status_code}"}
        except Exception as e:
            logger.exception("DashScope request failed")
            return {"success": False, "text": "", "error": str(e)}
