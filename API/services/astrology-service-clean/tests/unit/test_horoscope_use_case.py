"""
Unit Tests for GetHoroscopeUseCase.

Tests horoscope use case with mock repository.
"""

import pytest
from datetime import date

from domain.entities import ZodiacSign, HoroscopePeriod
from application.use_cases import GetHoroscopeUseCase
from application.use_cases.get_horoscope import (
    HoroscopeValidationError,
    HoroscopeNotFoundError
)
from infrastructure.repositories import MockHoroscopeRepository


class TestGetHoroscopeUseCase:
    """Test suite for horoscope use case."""

    @pytest.fixture
    def mock_repository(self):
        return MockHoroscopeRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetHoroscopeUseCase(horoscope_repository=mock_repository)

    # =========================================================================
    # Success Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_horoscope_success_english(self, use_case):
        """Test successful horoscope lookup with English sign."""
        result = await use_case.execute("Aries", "daily")

        assert result.success is True
        assert result.sign == "Aries"
        assert result.sign_hindi == "मेष"
        assert result.period == "daily"
        assert 0 <= result.overall_score <= 100

    @pytest.mark.asyncio
    async def test_get_horoscope_success_hindi(self, use_case):
        """Test successful horoscope lookup with Hindi sign."""
        result = await use_case.execute("मेष", "daily")

        assert result.success is True
        assert result.sign == "Aries"
        assert result.sign_hindi == "मेष"

    @pytest.mark.asyncio
    async def test_get_weekly_horoscope(self, use_case):
        """Test weekly horoscope."""
        result = await use_case.execute("Leo", "weekly")

        assert result.success is True
        assert result.period == "weekly"

    @pytest.mark.asyncio
    async def test_get_monthly_horoscope(self, use_case):
        """Test monthly horoscope."""
        result = await use_case.execute("Scorpio", "monthly")

        assert result.success is True
        assert result.period == "monthly"

    @pytest.mark.asyncio
    async def test_horoscope_has_scores(self, use_case):
        """Test that horoscope includes all scores."""
        result = await use_case.execute("Taurus", "daily")

        assert 0 <= result.love_score <= 100
        assert 0 <= result.career_score <= 100
        assert 0 <= result.health_score <= 100
        assert 0 <= result.finance_score <= 100

    @pytest.mark.asyncio
    async def test_horoscope_has_lucky_elements(self, use_case):
        """Test that horoscope includes lucky elements."""
        result = await use_case.execute("Gemini", "daily")

        assert result.lucky is not None
        assert len(result.lucky.numbers) > 0
        assert len(result.lucky.colors) > 0

    # =========================================================================
    # Validation Error Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_invalid_sign(self, use_case):
        """Test with invalid zodiac sign."""
        with pytest.raises(HoroscopeValidationError) as exc_info:
            await use_case.execute("InvalidSign", "daily")

        assert "Invalid zodiac sign" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_sign(self, use_case):
        """Test with empty sign."""
        with pytest.raises(HoroscopeValidationError) as exc_info:
            await use_case.execute("", "daily")

        assert "required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_period(self, use_case):
        """Test with invalid period."""
        with pytest.raises(HoroscopeValidationError) as exc_info:
            await use_case.execute("Aries", "hourly")  # Not supported

        assert "Invalid period" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_date_format(self, use_case):
        """Test with invalid date format."""
        with pytest.raises(HoroscopeValidationError) as exc_info:
            await use_case.execute("Aries", "daily", "04-02-2026")  # Wrong format

        assert "Invalid date format" in str(exc_info.value)


class TestZodiacSignEntity:
    """Test ZodiacSign entity."""

    def test_from_string_english(self):
        """Test parsing English sign name."""
        sign = ZodiacSign.from_string("aries")
        assert sign == ZodiacSign.ARIES

    def test_from_string_hindi(self):
        """Test parsing Hindi sign name."""
        sign = ZodiacSign.from_string("मेष")
        assert sign == ZodiacSign.ARIES

    def test_from_string_invalid(self):
        """Test parsing invalid sign name."""
        with pytest.raises(ValueError):
            ZodiacSign.from_string("NotASign")

    def test_element(self):
        """Test element property."""
        assert ZodiacSign.ARIES.element == "Fire"
        assert ZodiacSign.TAURUS.element == "Earth"
        assert ZodiacSign.GEMINI.element == "Air"
        assert ZodiacSign.CANCER.element == "Water"

    def test_ruling_planet(self):
        """Test ruling planet property."""
        assert ZodiacSign.ARIES.ruling_planet == "Mars"
        assert ZodiacSign.LEO.ruling_planet == "Sun"
