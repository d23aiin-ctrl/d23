"""Data Transfer Objects for Vision Service API."""

from pydantic import BaseModel, Field


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis endpoints."""
    image_base64: str = Field(..., description="Base64 encoded image data")
    language: str = Field(default="en", description="Response language (en, hi, etc.)")


class CustomQueryRequest(BaseModel):
    """Request model for custom image queries."""
    image_base64: str = Field(..., description="Base64 encoded image data")
    query: str = Field(..., description="Question to ask about the image")
    language: str = Field(default="en", description="Response language")


class ImageDescriptionResponse(BaseModel):
    """Response for image description."""
    success: bool
    description: str
    provider: str = ""
    error: str = ""


class TextExtractionResponse(BaseModel):
    """Response for OCR/text extraction."""
    success: bool
    text: str
    confidence: float = 0.0
    language: str = ""
    provider: str = ""
    error: str = ""


class DetectedObjectDTO(BaseModel):
    """A detected object."""
    name: str
    confidence: float = 0.0


class ObjectDetectionResponse(BaseModel):
    """Response for object detection."""
    success: bool
    objects: list[DetectedObjectDTO] = []
    count: int = 0
    provider: str = ""
    error: str = ""


class DocumentAnalysisResponse(BaseModel):
    """Response for document analysis."""
    success: bool
    document_type: str = ""
    title: str = ""
    extracted_fields: dict = {}
    raw_text: str = ""
    language: str = ""
    provider: str = ""
    error: str = ""


class ReceiptItemDTO(BaseModel):
    """A line item from a receipt."""
    name: str
    quantity: int = 1
    price: float = 0.0


class ReceiptAnalysisResponse(BaseModel):
    """Response for receipt analysis."""
    success: bool
    merchant_name: str = ""
    date: str = ""
    total_amount: float = 0.0
    currency: str = "INR"
    items: list[ReceiptItemDTO] = []
    tax: float = 0.0
    payment_method: str = ""
    provider: str = ""
    error: str = ""


class FoodIdentificationResponse(BaseModel):
    """Response for food identification."""
    success: bool
    items: list[str] = []
    cuisine_type: str = ""
    is_vegetarian: bool | None = None
    estimated_calories: int | None = None
    description: str = ""
    provider: str = ""
    error: str = ""


class CustomQueryResponse(BaseModel):
    """Response for custom image queries."""
    success: bool
    query: str
    response: str
    provider: str = ""
    error: str = ""
