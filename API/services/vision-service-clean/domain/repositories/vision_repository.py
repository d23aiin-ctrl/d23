"""Abstract repository interface for vision/image analysis operations."""

from abc import ABC, abstractmethod

from domain.entities.image_analysis import ImageAnalysisResult


class VisionRepository(ABC):
    """Abstract interface for vision model backends (DashScope, Ollama, etc.)."""

    @abstractmethod
    async def describe_image(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        """Generate a description of the image."""
        pass

    @abstractmethod
    async def extract_text(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        """Extract text from the image (OCR)."""
        pass

    @abstractmethod
    async def detect_objects(self, image_base64: str) -> ImageAnalysisResult:
        """Detect and list objects in the image."""
        pass

    @abstractmethod
    async def analyze_document(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        """Analyze a document image and extract structured information."""
        pass

    @abstractmethod
    async def analyze_receipt(self, image_base64: str) -> ImageAnalysisResult:
        """Analyze a receipt/bill image and extract transaction details."""
        pass

    @abstractmethod
    async def identify_food(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        """Identify food items in the image."""
        pass

    @abstractmethod
    async def custom_query(self, image_base64: str, query: str, language: str = "en") -> ImageAnalysisResult:
        """Answer a custom question about the image."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the backend is available."""
        pass
