"""Use case for analyzing images with vision models."""

from dataclasses import dataclass

from domain.entities.image_analysis import AnalysisType, ImageAnalysisResult
from domain.repositories.vision_repository import VisionRepository
from application.dto.vision_dto import (
    ImageDescriptionResponse,
    TextExtractionResponse,
    ObjectDetectionResponse,
    DocumentAnalysisResponse,
    ReceiptAnalysisResponse,
    FoodIdentificationResponse,
    CustomQueryResponse,
    DetectedObjectDTO,
    ReceiptItemDTO,
)


@dataclass
class AnalyzeImageUseCase:
    """Use case for performing various image analysis operations."""

    primary_repository: VisionRepository
    fallback_repository: VisionRepository | None = None

    async def _get_repository(self) -> VisionRepository:
        """Get available repository, falling back if primary is unavailable."""
        if await self.primary_repository.is_available():
            return self.primary_repository
        if self.fallback_repository and await self.fallback_repository.is_available():
            return self.fallback_repository
        return self.primary_repository  # Will fail with appropriate error

    async def describe(self, image_base64: str, language: str = "en") -> ImageDescriptionResponse:
        """Describe the contents of an image."""
        repo = await self._get_repository()
        result = await repo.describe_image(image_base64, language)
        return ImageDescriptionResponse(
            success=result.success,
            description=result.description,
            provider=result.provider,
            error=result.error,
        )

    async def extract_text(self, image_base64: str, language: str = "en") -> TextExtractionResponse:
        """Extract text from an image (OCR)."""
        repo = await self._get_repository()
        result = await repo.extract_text(image_base64, language)

        text = ""
        confidence = 0.0
        detected_lang = ""

        if result.extracted_text:
            text = result.extracted_text.text
            confidence = result.extracted_text.confidence
            detected_lang = result.extracted_text.language

        return TextExtractionResponse(
            success=result.success,
            text=text,
            confidence=confidence,
            language=detected_lang,
            provider=result.provider,
            error=result.error,
        )

    async def detect_objects(self, image_base64: str) -> ObjectDetectionResponse:
        """Detect objects in an image."""
        repo = await self._get_repository()
        result = await repo.detect_objects(image_base64)

        objects = [
            DetectedObjectDTO(name=obj.name, confidence=obj.confidence)
            for obj in result.detected_objects
        ]

        return ObjectDetectionResponse(
            success=result.success,
            objects=objects,
            count=len(objects),
            provider=result.provider,
            error=result.error,
        )

    async def analyze_document(self, image_base64: str, language: str = "en") -> DocumentAnalysisResponse:
        """Analyze a document image."""
        repo = await self._get_repository()
        result = await repo.analyze_document(image_base64, language)

        doc = result.document_info
        return DocumentAnalysisResponse(
            success=result.success,
            document_type=doc.document_type if doc else "",
            title=doc.title if doc else "",
            extracted_fields=doc.extracted_fields if doc else {},
            raw_text=doc.raw_text if doc else "",
            language=doc.language if doc else "",
            provider=result.provider,
            error=result.error,
        )

    async def analyze_receipt(self, image_base64: str) -> ReceiptAnalysisResponse:
        """Analyze a receipt/bill image."""
        repo = await self._get_repository()
        result = await repo.analyze_receipt(image_base64)

        receipt = result.receipt_info
        items = []
        if receipt and receipt.items:
            items = [
                ReceiptItemDTO(
                    name=item.get("name", ""),
                    quantity=item.get("quantity", 1),
                    price=item.get("price", 0.0),
                )
                for item in receipt.items
            ]

        return ReceiptAnalysisResponse(
            success=result.success,
            merchant_name=receipt.merchant_name if receipt else "",
            date=receipt.date if receipt else "",
            total_amount=receipt.total_amount if receipt else 0.0,
            currency=receipt.currency if receipt else "INR",
            items=items,
            tax=receipt.tax if receipt else 0.0,
            payment_method=receipt.payment_method if receipt else "",
            provider=result.provider,
            error=result.error,
        )

    async def identify_food(self, image_base64: str, language: str = "en") -> FoodIdentificationResponse:
        """Identify food items in an image."""
        repo = await self._get_repository()
        result = await repo.identify_food(image_base64, language)

        food = result.food_info
        return FoodIdentificationResponse(
            success=result.success,
            items=food.items if food else [],
            cuisine_type=food.cuisine_type if food else "",
            is_vegetarian=food.is_vegetarian if food else None,
            estimated_calories=food.estimated_calories if food else None,
            description=food.description if food else "",
            provider=result.provider,
            error=result.error,
        )

    async def custom_query(self, image_base64: str, query: str, language: str = "en") -> CustomQueryResponse:
        """Answer a custom question about an image."""
        repo = await self._get_repository()
        result = await repo.custom_query(image_base64, query, language)

        return CustomQueryResponse(
            success=result.success,
            query=query,
            response=result.custom_response or result.description,
            provider=result.provider,
            error=result.error,
        )

    async def check_availability(self) -> dict:
        """Check which backends are available."""
        primary_available = await self.primary_repository.is_available()
        fallback_available = False
        if self.fallback_repository:
            fallback_available = await self.fallback_repository.is_available()

        return {
            "primary_available": primary_available,
            "fallback_available": fallback_available,
            "any_available": primary_available or fallback_available,
        }
