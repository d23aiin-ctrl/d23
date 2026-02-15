"""
Get Panchang Use Case.

Single responsibility: Get Hindu calendar for a date and location.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from domain.entities import Panchang
from domain.repositories import PanchangRepository
from application.dto import PanchangRequest, PanchangResponse, TithiDTO, MuhurtaDTO


class PanchangValidationError(Exception):
    """Raised when panchang request validation fails."""
    pass


class PanchangNotFoundError(Exception):
    """Raised when panchang is not available."""
    pass


@dataclass
class GetPanchangUseCase:
    """
    Use case for getting panchang.

    Validates input, fetches calendar data, transforms to DTO.
    """
    panchang_repository: PanchangRepository

    async def execute(self, request: PanchangRequest) -> PanchangResponse:
        """
        Execute the use case.

        Args:
            request: PanchangRequest with date and location

        Returns:
            PanchangResponse DTO

        Raises:
            PanchangValidationError: If input is invalid
            PanchangNotFoundError: If panchang not available
        """
        # 1. Parse and validate input
        target_date = self._parse_date(request.date)
        self._validate_coordinates(request.latitude, request.longitude)

        # 2. Fetch from repository
        panchang = await self.panchang_repository.get_panchang(
            target_date=target_date,
            city=request.city,
            latitude=request.latitude,
            longitude=request.longitude
        )

        if panchang is None:
            raise PanchangNotFoundError(
                f"Panchang not available for {target_date}"
            )

        # 3. Transform to DTO
        return self._to_response(panchang)

    def _parse_date(self, date_str: Optional[str]) -> date:
        """Parse date string or return today."""
        if not date_str:
            return date.today()

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise PanchangValidationError(
                f"Invalid date format: {date_str}. Use YYYY-MM-DD"
            )

    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """Validate latitude and longitude."""
        if not -90 <= lat <= 90:
            raise PanchangValidationError("Invalid latitude")
        if not -180 <= lon <= 180:
            raise PanchangValidationError("Invalid longitude")

    def _to_response(self, panchang: Panchang) -> PanchangResponse:
        """Transform domain entity to DTO."""
        tithi_dto = TithiDTO(
            number=panchang.tithi.number,
            name=panchang.tithi.name,
            name_hindi=panchang.tithi.hindi_name,
            paksha=panchang.tithi.paksha.value,
            end_time=panchang.tithi.end_time.strftime("%H:%M"),
            is_auspicious=panchang.tithi.is_auspicious
        )

        abhijit = None
        if panchang.abhijit_muhurta:
            abhijit = MuhurtaDTO(
                name=panchang.abhijit_muhurta.name,
                start_time=panchang.abhijit_muhurta.start_time.strftime("%H:%M"),
                end_time=panchang.abhijit_muhurta.end_time.strftime("%H:%M"),
                is_auspicious=panchang.abhijit_muhurta.is_auspicious,
                suitable_for=panchang.abhijit_muhurta.suitable_for
            )

        rahukaal = None
        if panchang.rahukaal:
            rahukaal = MuhurtaDTO(
                name=panchang.rahukaal.name,
                start_time=panchang.rahukaal.start_time.strftime("%H:%M"),
                end_time=panchang.rahukaal.end_time.strftime("%H:%M"),
                is_auspicious=False,
                suitable_for=[]
            )

        yamaganda = None
        if panchang.yamaganda:
            yamaganda = MuhurtaDTO(
                name=panchang.yamaganda.name,
                start_time=panchang.yamaganda.start_time.strftime("%H:%M"),
                end_time=panchang.yamaganda.end_time.strftime("%H:%M"),
                is_auspicious=False,
                suitable_for=[]
            )

        return PanchangResponse(
            success=True,
            date=panchang.date.strftime("%Y-%m-%d"),
            day=panchang.vara,
            day_hindi=panchang.vara_hindi,
            city=panchang.city,
            hindu_month=panchang.hindu_month,
            hindu_month_hindi=panchang.hindu_month_hindi,
            hindu_year=panchang.hindu_year,
            tithi=tithi_dto,
            nakshatra=panchang.nakshatra_name,
            nakshatra_hindi=panchang.nakshatra_hindi,
            nakshatra_end_time=panchang.nakshatra_end_time.strftime("%H:%M"),
            yoga=panchang.yoga.name,
            yoga_hindi=panchang.yoga.hindi_name,
            yoga_end_time=panchang.yoga.end_time.strftime("%H:%M"),
            karana=panchang.karana.name,
            karana_hindi=panchang.karana.hindi_name,
            sunrise=panchang.sunrise.strftime("%H:%M"),
            sunset=panchang.sunset.strftime("%H:%M"),
            moonrise=panchang.moonrise.strftime("%H:%M") if panchang.moonrise else None,
            moonset=panchang.moonset.strftime("%H:%M") if panchang.moonset else None,
            abhijit_muhurta=abhijit,
            rahukaal=rahukaal,
            yamaganda=yamaganda,
            is_auspicious_day=panchang.is_auspicious_day,
            is_ekadashi=panchang.is_ekadashi,
            is_pradosh=panchang.is_pradosh,
            is_amavasya=panchang.is_amavasya,
            is_purnima=panchang.is_purnima,
            festivals=panchang.festivals
        )
