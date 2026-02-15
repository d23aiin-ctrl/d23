"""
Get Horoscope Use Case.

Single responsibility: Get horoscope prediction for a zodiac sign.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from domain.entities import ZodiacSign, HoroscopePeriod, Horoscope
from domain.repositories import HoroscopeRepository
from application.dto import HoroscopeResponse, LuckyElementsDTO


class HoroscopeValidationError(Exception):
    """Raised when horoscope request validation fails."""
    pass


class HoroscopeNotFoundError(Exception):
    """Raised when horoscope is not available."""
    pass


@dataclass
class GetHoroscopeUseCase:
    """
    Use case for getting horoscope.

    Validates input, fetches prediction, transforms to DTO.
    """
    horoscope_repository: HoroscopeRepository

    async def execute(
        self,
        sign: str,
        period: str = "daily",
        target_date: Optional[str] = None
    ) -> HoroscopeResponse:
        """
        Execute the use case.

        Args:
            sign: Zodiac sign (English or Hindi)
            period: daily/weekly/monthly
            target_date: Date string (YYYY-MM-DD)

        Returns:
            HoroscopeResponse DTO

        Raises:
            HoroscopeValidationError: If input is invalid
            HoroscopeNotFoundError: If horoscope not available
        """
        # 1. Validate and parse input
        zodiac_sign = self._parse_sign(sign)
        horoscope_period = self._parse_period(period)
        parsed_date = self._parse_date(target_date)

        # 2. Fetch from repository
        horoscope = await self.horoscope_repository.get_horoscope(
            zodiac_sign, horoscope_period, parsed_date
        )

        if horoscope is None:
            raise HoroscopeNotFoundError(
                f"Horoscope not available for {sign} ({period})"
            )

        # 3. Transform to DTO
        return self._to_response(horoscope)

    def _parse_sign(self, sign: str) -> ZodiacSign:
        """Parse and validate zodiac sign."""
        if not sign:
            raise HoroscopeValidationError("Zodiac sign is required")

        try:
            return ZodiacSign.from_string(sign)
        except ValueError:
            raise HoroscopeValidationError(
                f"Invalid zodiac sign: {sign}. "
                "Use English (Aries) or Hindi (मेष)"
            )

    def _parse_period(self, period: str) -> HoroscopePeriod:
        """Parse and validate period."""
        period_lower = period.lower()
        try:
            return HoroscopePeriod(period_lower)
        except ValueError:
            raise HoroscopeValidationError(
                f"Invalid period: {period}. Use daily/weekly/monthly"
            )

    def _parse_date(self, date_str: Optional[str]) -> date:
        """Parse date string or return today."""
        if not date_str:
            return date.today()

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HoroscopeValidationError(
                f"Invalid date format: {date_str}. Use YYYY-MM-DD"
            )

    def _to_response(self, horoscope: Horoscope) -> HoroscopeResponse:
        """Transform domain entity to DTO."""
        lucky_dto = None
        if horoscope.lucky:
            lucky_dto = LuckyElementsDTO(
                numbers=horoscope.lucky.numbers,
                colors=horoscope.lucky.colors,
                time=horoscope.lucky.time,
                day=horoscope.lucky.day
            )

        return HoroscopeResponse(
            success=True,
            sign=horoscope.sign.english,
            sign_hindi=horoscope.sign.hindi,
            period=horoscope.period.value,
            date=horoscope.date.strftime("%Y-%m-%d"),
            prediction=horoscope.prediction,
            overall_score=horoscope.overall_score,
            love_score=horoscope.love_score,
            career_score=horoscope.career_score,
            health_score=horoscope.health_score,
            finance_score=horoscope.finance_score,
            love_prediction=horoscope.love_prediction,
            career_prediction=horoscope.career_prediction,
            health_prediction=horoscope.health_prediction,
            finance_prediction=horoscope.finance_prediction,
            mood=horoscope.mood,
            health_tip=horoscope.health_tip,
            lucky=lucky_dto,
            compatible_signs=[s.english for s in horoscope.compatible_signs]
        )
