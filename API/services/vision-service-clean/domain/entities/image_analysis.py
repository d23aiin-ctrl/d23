"""Domain entities for image analysis results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AnalysisType(str, Enum):
    DESCRIBE = "describe"
    EXTRACT_TEXT = "extract_text"
    DETECT_OBJECTS = "detect_objects"
    ANALYZE_DOCUMENT = "analyze_document"
    ANALYZE_RECEIPT = "analyze_receipt"
    IDENTIFY_FOOD = "identify_food"
    CUSTOM_QUERY = "custom_query"


@dataclass
class ExtractedText:
    """Text extracted from an image via OCR."""
    text: str
    confidence: float = 0.0
    language: str = ""
    regions: list[dict] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass
class DetectedObject:
    """An object detected in an image."""
    name: str
    confidence: float = 0.0
    bounding_box: dict | None = None
    attributes: dict = field(default_factory=dict)


@dataclass
class DocumentInfo:
    """Information extracted from a document image."""
    document_type: str = ""
    title: str = ""
    extracted_fields: dict = field(default_factory=dict)
    raw_text: str = ""
    language: str = ""


@dataclass
class ReceiptInfo:
    """Information extracted from a receipt/bill image."""
    merchant_name: str = ""
    date: str = ""
    total_amount: float = 0.0
    currency: str = "INR"
    items: list[dict] = field(default_factory=list)
    tax: float = 0.0
    payment_method: str = ""
    raw_text: str = ""


@dataclass
class FoodInfo:
    """Information about food items in an image."""
    items: list[str] = field(default_factory=list)
    cuisine_type: str = ""
    is_vegetarian: bool | None = None
    estimated_calories: int | None = None
    description: str = ""


@dataclass
class ImageAnalysisResult:
    """Result of any image analysis operation."""
    success: bool
    analysis_type: AnalysisType
    description: str = ""
    extracted_text: ExtractedText | None = None
    detected_objects: list[DetectedObject] = field(default_factory=list)
    document_info: DocumentInfo | None = None
    receipt_info: ReceiptInfo | None = None
    food_info: FoodInfo | None = None
    custom_response: str = ""
    raw_response: Any = None
    error: str = ""
    provider: str = ""  # "dashscope" or "ollama"

    @property
    def has_error(self) -> bool:
        return bool(self.error)
