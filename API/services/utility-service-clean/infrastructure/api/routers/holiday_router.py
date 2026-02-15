"""Holiday API Router."""
from fastapi import APIRouter, Depends
from typing import Optional
from application.dto import HolidayRequest, HolidayResponse
from application.dto.holiday_dto import HolidayTypeDTO
from application.use_cases import GetHolidaysUseCase
from infrastructure.api.dependencies import get_holidays_use_case

router = APIRouter(prefix="/holidays", tags=["Holidays"])


@router.get("/", response_model=HolidayResponse)
async def get_holidays(
    year: int = 2024,
    state: Optional[str] = None,
    holiday_type: Optional[HolidayTypeDTO] = None,
    use_case: GetHolidaysUseCase = Depends(get_holidays_use_case)
) -> HolidayResponse:
    """Get holidays for year."""
    request = HolidayRequest(year=year, state=state, holiday_type=holiday_type)
    return await use_case.execute(request)
