"""Client for Vision Service (port 8009)."""

from clients.base_client import BaseServiceClient


class VisionClient(BaseServiceClient):
    """Async client for the Vision microservice."""

    def __init__(self, base_url: str = "http://localhost:8009", **kwargs):
        super().__init__(base_url, service_name="Vision Service", **kwargs)

    async def describe_image(self, image_base64: str, language: str = "en") -> dict:
        return await self.post("/describe", json={
            "image_base64": image_base64,
            "language": language,
        })

    async def extract_text(self, image_base64: str, language: str = "en") -> dict:
        return await self.post("/extract-text", json={
            "image_base64": image_base64,
            "language": language,
        })

    async def detect_objects(self, image_base64: str) -> dict:
        return await self.post("/detect-objects", json={
            "image_base64": image_base64,
        })

    async def analyze_document(self, image_base64: str, language: str = "en") -> dict:
        return await self.post("/analyze-document", json={
            "image_base64": image_base64,
            "language": language,
        })

    async def analyze_receipt(self, image_base64: str) -> dict:
        return await self.post("/analyze-receipt", json={
            "image_base64": image_base64,
        })

    async def identify_food(self, image_base64: str, language: str = "en") -> dict:
        return await self.post("/identify-food", json={
            "image_base64": image_base64,
            "language": language,
        })

    async def custom_query(self, image_base64: str, query: str, language: str = "en") -> dict:
        return await self.post("/query", json={
            "image_base64": image_base64,
            "query": query,
            "language": language,
        })

    async def check_availability(self) -> dict:
        return await self.get("/availability")
