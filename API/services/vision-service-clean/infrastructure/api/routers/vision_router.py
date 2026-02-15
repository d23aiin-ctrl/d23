"""API routes for Vision Service."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from application.dto.vision_dto import (
    ImageAnalysisRequest,
    ImageDescriptionResponse,
    TextExtractionResponse,
    ObjectDetectionResponse,
    DocumentAnalysisResponse,
    ReceiptAnalysisResponse,
    FoodIdentificationResponse,
    CustomQueryRequest,
    CustomQueryResponse,
)
from application.use_cases.analyze_image import AnalyzeImageUseCase
from infrastructure.api.dependencies import get_analyze_use_case

router = APIRouter()


@router.post("/describe", response_model=ImageDescriptionResponse)
async def describe_image(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Describe the contents of an image."""
    try:
        return await use_case.describe(request.image_base64, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-text", response_model=TextExtractionResponse)
async def extract_text(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Extract text from an image (OCR)."""
    try:
        return await use_case.extract_text(request.image_base64, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-objects", response_model=ObjectDetectionResponse)
async def detect_objects(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Detect objects in an image."""
    try:
        return await use_case.detect_objects(request.image_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Analyze a document image and extract structured information."""
    try:
        return await use_case.analyze_document(request.image_base64, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-receipt", response_model=ReceiptAnalysisResponse)
async def analyze_receipt(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Analyze a receipt/bill image and extract transaction details."""
    try:
        return await use_case.analyze_receipt(request.image_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify-food", response_model=FoodIdentificationResponse)
async def identify_food(
    request: ImageAnalysisRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Identify food items in an image."""
    try:
        return await use_case.identify_food(request.image_base64, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=CustomQueryResponse)
async def custom_query(
    request: CustomQueryRequest,
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Answer a custom question about an image."""
    try:
        return await use_case.custom_query(request.image_base64, request.query, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability")
async def check_availability(
    use_case: Annotated[AnalyzeImageUseCase, Depends(get_analyze_use_case)],
):
    """Check which vision backends are available."""
    return await use_case.check_availability()
