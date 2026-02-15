"""
Panchang API Router.

Hindu calendar endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, Optional

from application.dto import PanchangRequest, PanchangResponse
from application.use_cases import GetPanchangUseCase
from application.use_cases.get_panchang import (
    PanchangValidationError,
    PanchangNotFoundError
)
from infrastructure.api.dependencies import get_panchang_use_case

router = APIRouter(prefix="/panchang", tags=["Panchang"])


@router.get(
    "",
    response_model=PanchangResponse,
    summary="Get Panchang",
    description="Get Hindu calendar for a date and location"
)
async def get_panchang(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), default today"),
    city: str = Query(default="Delhi"),
    latitude: float = Query(default=28.6139),
    longitude: float = Query(default=77.2090),
    use_case: Annotated[GetPanchangUseCase, Depends(get_panchang_use_case)] = None
):
    """
    Get Panchang (Hindu calendar).

    Returns five limbs (Panch-Ang):
    - **Tithi**: Lunar day
    - **Nakshatra**: Lunar mansion
    - **Yoga**: Sun-Moon combination
    - **Karana**: Half-tithi
    - **Vara**: Weekday

    Also includes muhurtas, sunrise/sunset, and festivals.
    """
    try:
        request = PanchangRequest(
            date=date,
            city=city,
            latitude=latitude,
            longitude=longitude
        )
        return await use_case.execute(request)
    except PanchangValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PanchangNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "",
    response_model=PanchangResponse,
    summary="Get Panchang (POST)",
    description="Get panchang with request body"
)
async def get_panchang_post(
    request: PanchangRequest,
    use_case: Annotated[GetPanchangUseCase, Depends(get_panchang_use_case)]
):
    """Get panchang using POST request."""
    try:
        return await use_case.execute(request)
    except PanchangValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PanchangNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
