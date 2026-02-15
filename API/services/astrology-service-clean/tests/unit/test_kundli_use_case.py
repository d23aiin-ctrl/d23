"""
Unit Tests for Kundli Use Cases.

Tests kundli generation and matching with mock repository.
"""

import pytest

from application.use_cases import GenerateKundliUseCase, MatchKundliUseCase
from application.use_cases.generate_kundli import (
    KundliValidationError,
    KundliGenerationError
)
from application.dto import KundliRequest, MatchingRequest
from infrastructure.repositories import MockKundliRepository


class TestGenerateKundliUseCase:
    """Test suite for kundli generation use case."""

    @pytest.fixture
    def mock_repository(self):
        return MockKundliRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GenerateKundliUseCase(kundli_repository=mock_repository)

    @pytest.fixture
    def valid_request(self):
        return KundliRequest(
            name="Test Person",
            date="1990-05-15",
            time="10:30",
            place="Delhi",
            latitude=28.6139,
            longitude=77.2090
        )

    # =========================================================================
    # Success Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_generate_kundli_success(self, use_case, valid_request):
        """Test successful kundli generation."""
        result = await use_case.execute(valid_request)

        assert result.success is True
        assert result.name == "Test Person"
        assert result.birth_date == "1990-05-15"
        assert result.birth_time == "10:30"
        assert result.lagna is not None
        assert result.moon_sign is not None
        assert result.sun_sign is not None

    @pytest.mark.asyncio
    async def test_kundli_has_planets(self, use_case, valid_request):
        """Test that kundli includes planet positions."""
        result = await use_case.execute(valid_request)

        assert len(result.planets) == 9  # 9 planets
        for planet in result.planets:
            assert planet.planet is not None
            assert planet.sign is not None
            assert 1 <= planet.house <= 12

    @pytest.mark.asyncio
    async def test_kundli_has_houses(self, use_case, valid_request):
        """Test that kundli includes 12 houses."""
        result = await use_case.execute(valid_request)

        assert len(result.houses) == 12
        for house in result.houses:
            assert 1 <= house.number <= 12

    @pytest.mark.asyncio
    async def test_kundli_has_doshas(self, use_case, valid_request):
        """Test that kundli includes dosha analysis."""
        result = await use_case.execute(valid_request)

        assert len(result.doshas) > 0
        for dosha in result.doshas:
            assert dosha.name is not None
            assert dosha.severity in ["None", "Mild", "Moderate", "Severe"]

    # =========================================================================
    # Validation Error Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_empty_name(self, use_case):
        """Test with empty name."""
        request = KundliRequest(
            name="  ",
            date="1990-05-15",
            time="10:30",
            place="Delhi",
            latitude=28.6139,
            longitude=77.2090
        )

        with pytest.raises(KundliValidationError) as exc_info:
            await use_case.execute(request)

        assert "Name is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_date(self, use_case):
        """Test with invalid date format."""
        request = KundliRequest(
            name="Test",
            date="15-05-1990",  # Wrong format
            time="10:30",
            place="Delhi",
            latitude=28.6139,
            longitude=77.2090
        )

        with pytest.raises(KundliValidationError) as exc_info:
            await use_case.execute(request)

        assert "Invalid date/time format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_latitude(self, use_case):
        """Test that invalid latitude is caught by Pydantic validation."""
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            KundliRequest(
                name="Test",
                date="1990-05-15",
                time="10:30",
                place="Delhi",
                latitude=100.0,  # Invalid - caught by Pydantic
                longitude=77.2090
            )


class TestMatchKundliUseCase:
    """Test suite for kundli matching use case."""

    @pytest.fixture
    def mock_repository(self):
        return MockKundliRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return MatchKundliUseCase(kundli_repository=mock_repository)

    @pytest.fixture
    def valid_request(self):
        person1 = KundliRequest(
            name="Person 1",
            date="1990-05-15",
            time="10:30",
            place="Delhi",
            latitude=28.6139,
            longitude=77.2090
        )
        person2 = KundliRequest(
            name="Person 2",
            date="1992-08-20",
            time="14:45",
            place="Mumbai",
            latitude=19.0760,
            longitude=72.8777
        )
        return MatchingRequest(person1=person1, person2=person2)

    @pytest.mark.asyncio
    async def test_match_kundlis_success(self, use_case, valid_request):
        """Test successful kundli matching."""
        result = await use_case.execute(valid_request)

        assert result.success is True
        assert 0 <= result.total_points <= 36
        assert result.max_points == 36
        assert 0 <= result.match_percentage <= 100

    @pytest.mark.asyncio
    async def test_match_has_guna_details(self, use_case, valid_request):
        """Test that matching includes guna details."""
        result = await use_case.execute(valid_request)

        assert len(result.guna_details) == 8  # Ashtakoot
        for guna in result.guna_details:
            assert guna.name is not None
            assert guna.obtained_points <= guna.max_points

    @pytest.mark.asyncio
    async def test_match_has_verdict(self, use_case, valid_request):
        """Test that matching includes verdict."""
        result = await use_case.execute(valid_request)

        assert result.verdict in ["Excellent", "Good", "Average", "Below Average"]
        assert isinstance(result.is_recommended, bool)
