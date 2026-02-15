"""Ollama-based implementation of VisionRepository."""

import logging
import re

from domain.entities.image_analysis import (
    AnalysisType,
    ImageAnalysisResult,
    ExtractedText,
    DetectedObject,
    DocumentInfo,
    ReceiptInfo,
    FoodInfo,
)
from domain.repositories.vision_repository import VisionRepository
from infrastructure.external.ollama_client import OllamaClient
from infrastructure.repositories.prompts import get_prompt

logger = logging.getLogger(__name__)


class OllamaVisionRepository(VisionRepository):
    """VisionRepository implementation using local Ollama with vision models."""

    def __init__(self, client: OllamaClient):
        self.client = client

    async def is_available(self) -> bool:
        return await self.client.is_available()

    async def describe_image(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        prompt = get_prompt("describe", language)
        result = await self.client.analyze(image_base64, prompt)

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.DESCRIBE,
            description=result.get("text", ""),
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def extract_text(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        prompt = get_prompt("extract_text", language)
        result = await self.client.analyze(image_base64, prompt)

        text = result.get("text", "")
        extracted = ExtractedText(
            text=text,
            confidence=0.85 if text and "no text" not in text.lower() else 0.0,
            language=language,
        )

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.EXTRACT_TEXT,
            extracted_text=extracted,
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def detect_objects(self, image_base64: str) -> ImageAnalysisResult:
        prompt = get_prompt("detect_objects")
        result = await self.client.analyze(image_base64, prompt)

        objects = []
        text = result.get("text", "")
        if text:
            lines = text.strip().split("\n")
            for line in lines:
                name = line.strip().strip("-").strip("•").strip("*").strip('"').strip()
                if name and len(name) > 1 and len(name) < 100:
                    objects.append(DetectedObject(name=name, confidence=0.75))

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.DETECT_OBJECTS,
            detected_objects=objects,
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def analyze_document(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        prompt = get_prompt("analyze_document", language)
        result = await self.client.analyze(image_base64, prompt)

        text = result.get("text", "")
        doc_info = self._parse_document_response(text)

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.ANALYZE_DOCUMENT,
            document_info=doc_info,
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def analyze_receipt(self, image_base64: str) -> ImageAnalysisResult:
        prompt = get_prompt("analyze_receipt")
        result = await self.client.analyze(image_base64, prompt)

        text = result.get("text", "")
        receipt_info = self._parse_receipt_response(text)

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.ANALYZE_RECEIPT,
            receipt_info=receipt_info,
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def identify_food(self, image_base64: str, language: str = "en") -> ImageAnalysisResult:
        prompt = get_prompt("identify_food", language)
        result = await self.client.analyze(image_base64, prompt)

        text = result.get("text", "")
        food_info = self._parse_food_response(text)

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.IDENTIFY_FOOD,
            food_info=food_info,
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    async def custom_query(self, image_base64: str, query: str, language: str = "en") -> ImageAnalysisResult:
        prompt = get_prompt("custom_query", language, query=query)
        result = await self.client.analyze(image_base64, prompt)

        return ImageAnalysisResult(
            success=result.get("success", False),
            analysis_type=AnalysisType.CUSTOM_QUERY,
            custom_response=result.get("text", ""),
            error=result.get("error", ""),
            provider=f"ollama:{result.get('model', 'unknown')}",
            raw_response=result.get("raw"),
        )

    # Parsing methods - same as DashScope implementation
    def _parse_document_response(self, text: str) -> DocumentInfo:
        doc = DocumentInfo()
        doc.raw_text = text

        lines = text.split("\n")
        in_fields = False
        fields = {}

        for line in lines:
            line = line.strip()
            if line.startswith("DOCUMENT_TYPE:"):
                doc.document_type = line.split(":", 1)[1].strip()
            elif line.startswith("TITLE:"):
                doc.title = line.split(":", 1)[1].strip()
            elif line.startswith("FIELDS:"):
                in_fields = True
            elif line.startswith("RAW_TEXT:"):
                in_fields = False
            elif in_fields and line.startswith("-"):
                parts = line[1:].split(":", 1)
                if len(parts) == 2:
                    fields[parts[0].strip()] = parts[1].strip()

        doc.extracted_fields = fields
        return doc

    def _parse_receipt_response(self, text: str) -> ReceiptInfo:
        receipt = ReceiptInfo()
        receipt.raw_text = text

        lines = text.split("\n")
        items = []

        for line in lines:
            line = line.strip()
            if line.startswith("MERCHANT:"):
                receipt.merchant_name = line.split(":", 1)[1].strip()
            elif line.startswith("DATE:"):
                receipt.date = line.split(":", 1)[1].strip()
            elif line.startswith("TOTAL:"):
                total_str = line.split(":", 1)[1].strip()
                receipt.total_amount = self._parse_amount(total_str)
            elif line.startswith("TAX:"):
                tax_str = line.split(":", 1)[1].strip()
                receipt.tax = self._parse_amount(tax_str)
            elif line.startswith("PAYMENT:"):
                receipt.payment_method = line.split(":", 1)[1].strip()
            elif line.startswith("-") and "@" in line:
                item = self._parse_receipt_item(line)
                if item:
                    items.append(item)

        receipt.items = items
        return receipt

    def _parse_receipt_item(self, line: str) -> dict | None:
        line = line.lstrip("-").strip()
        match = re.match(r"(.+?)\s*x?(\d+)?\s*@\s*([\d.,]+)", line)
        if match:
            return {
                "name": match.group(1).strip(),
                "quantity": int(match.group(2) or 1),
                "price": self._parse_amount(match.group(3)),
            }
        return None

    def _parse_amount(self, text: str) -> float:
        text = re.sub(r"[^\d.,]", "", text)
        text = text.replace(",", "")
        try:
            return float(text) if text else 0.0
        except ValueError:
            return 0.0

    def _parse_food_response(self, text: str) -> FoodInfo:
        food = FoodInfo()
        food.description = text

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("ITEMS:"):
                items_str = line.split(":", 1)[1].strip()
                food.items = [i.strip() for i in items_str.split(",") if i.strip()]
            elif line.startswith("CUISINE:"):
                food.cuisine_type = line.split(":", 1)[1].strip()
            elif line.startswith("VEGETARIAN:"):
                veg_str = line.split(":", 1)[1].strip().lower()
                if veg_str == "yes":
                    food.is_vegetarian = True
                elif veg_str == "no":
                    food.is_vegetarian = False
            elif line.startswith("CALORIES:"):
                cal_str = line.split(":", 1)[1].strip()
                match = re.search(r"(\d+)", cal_str)
                if match:
                    food.estimated_calories = int(match.group(1))

        return food
