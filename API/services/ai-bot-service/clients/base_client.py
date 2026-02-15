"""Base async HTTP client with retry and error handling."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ServiceUnavailableError(Exception):
    """Raised when a downstream service is unreachable."""

    def __init__(self, service_name: str, detail: str = ""):
        self.service_name = service_name
        self.detail = detail
        super().__init__(f"{service_name} is currently unavailable. {detail}")


class BaseServiceClient:
    """Async HTTP client for calling downstream microservices."""

    def __init__(self, base_url: str, service_name: str, timeout: float = 30.0, max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={"Accept": "application/json"},
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict:
        return await self._request("POST", path, json=json)

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError as e:
                last_error = e
                logger.warning(
                    "%s connection failed (attempt %d/%d): %s",
                    self.service_name, attempt + 1, self.max_retries + 1, e,
                )
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    "%s request timed out (attempt %d/%d): %s",
                    self.service_name, attempt + 1, self.max_retries + 1, e,
                )
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    try:
                        detail = e.response.json()
                    except Exception:
                        detail = e.response.text
                    return {"error": True, "status_code": e.response.status_code, "detail": detail}
                last_error = e
                logger.warning(
                    "%s returned %d (attempt %d/%d)",
                    self.service_name, e.response.status_code, attempt + 1, self.max_retries + 1,
                )

        raise ServiceUnavailableError(
            self.service_name,
            detail=str(last_error) if last_error else "Max retries exceeded",
        )

    async def health_check(self) -> dict:
        try:
            result = await self.get("/health")
            return {"service": self.service_name, "status": "healthy", "data": result}
        except Exception as e:
            return {"service": self.service_name, "status": "unhealthy", "error": str(e)}
