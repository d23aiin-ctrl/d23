"""
Horoscope API Router.

Thin HTTP layer that delegates to use cases.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, Optional

from application.dto import HoroscopeRequest, HoroscopeResponse
from application.use_cases import GetHoroscopeUseCase
from application.use_cases.get_horoscope import (
    HoroscopeValidationError,
    HoroscopeNotFoundError
)
from infrastructure.api.dependencies import get_horoscope_use_case

router = APIRouter(prefix="/horoscope", tags=["Horoscope"])


@router.post(
    "",
    response_model=HoroscopeResponse,
    summary="Get Horoscope",
    description="Get horoscope prediction for a zodiac sign"
)
async def get_horoscope(
    request: HoroscopeRequest,
    use_case: Annotated[GetHoroscopeUseCase, Depends(get_horoscope_use_case)]
):
    """
    Get horoscope prediction.

    - **sign**: Zodiac sign (English: Aries, or Hindi: मेष)
    - **period**: daily, weekly, or monthly
    - **date**: Optional date (YYYY-MM-DD)
    """
    try:
        return await use_case.execute(
            sign=request.sign,
            period=request.period,
            target_date=request.date
        )
    except HoroscopeValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HoroscopeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{sign}",
    response_model=HoroscopeResponse,
    summary="Get Daily Horoscope",
    description="Get daily horoscope by sign"
)
async def get_daily_horoscope(
    sign: str,
    period: Optional[str] = Query(default="daily"),
    use_case: Annotated[GetHoroscopeUseCase, Depends(get_horoscope_use_case)] = None
):
    """
    Get daily horoscope for a sign.

    - **sign**: Zodiac sign (path parameter)
    """
    try:
        return await use_case.execute(sign=sign, period=period)
    except HoroscopeValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HoroscopeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
