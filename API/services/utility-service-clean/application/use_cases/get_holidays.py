"""Get Holidays Use Case."""
from domain.repositories import HolidayRepository
from domain.entities import HolidayType
from application.dto import HolidayRequest, HolidayResponse
from application.dto.holiday_dto import HolidayDTO, HolidayTypeDTO


class GetHolidaysUseCase:
    """Use case for getting holidays."""

    def __init__(self, holiday_repository: HolidayRepository):
        self.holiday_repository = holiday_repository

    def _map_holiday_type(self, holiday_type_dto: HolidayTypeDTO) -> HolidayType:
        mapping = {
            HolidayTypeDTO.NATIONAL: HolidayType.NATIONAL,
            HolidayTypeDTO.REGIONAL: HolidayType.REGIONAL,
            HolidayTypeDTO.BANK: HolidayType.BANK,
            HolidayTypeDTO.OPTIONAL: HolidayType.OPTIONAL,
        }
        return mapping.get(holiday_type_dto)

    async def execute(self, request: HolidayRequest) -> HolidayResponse:
        """Get holidays for year."""
        holiday_type = None
        if request.holiday_type:
            holiday_type = self._map_holiday_type(request.holiday_type)

        holidays = await self.holiday_repository.get_holidays(
            year=request.year,
            state=request.state,
            holiday_type=holiday_type
        )

        return HolidayResponse(
            success=True,
            data=[
                HolidayDTO(
                    name=h.name,
                    date=h.date,
                    holiday_type=h.holiday_type.value,
                    day=h.day,
                    description=h.description,
                    state=h.state
                )
                for h in holidays
            ]
        )
