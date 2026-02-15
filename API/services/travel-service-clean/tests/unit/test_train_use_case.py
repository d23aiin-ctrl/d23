"""
Unit Tests for Train Use Cases.

Tests for:
- GetTrainScheduleUseCase
- SearchTrainsUseCase
"""

import pytest

from application.use_cases import GetTrainScheduleUseCase, SearchTrainsUseCase
from application.use_cases.get_train_schedule import TrainValidationError, TrainNotFoundError
from application.use_cases.search_trains import StationValidationError
from infrastructure.repositories import MockTrainRepository


class TestGetTrainScheduleUseCase:
    """Test suite for train schedule use case."""

    @pytest.fixture
    def mock_repository(self):
        return MockTrainRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetTrainScheduleUseCase(train_repository=mock_repository)

    @pytest.mark.asyncio
    async def test_get_schedule_success(self, use_case):
        """Test successful schedule retrieval."""
        result = await use_case.execute("12301")

        assert result.success is True
        assert result.train.train_number == "12301"
        assert result.train.train_name == "Howrah Rajdhani Express"
        assert result.total_stops == 5
        assert result.stops[0].station_code == "NDLS"
        assert result.stops[-1].station_code == "HWH"

    @pytest.mark.asyncio
    async def test_invalid_train_number(self, use_case):
        """Test validation for invalid train number."""
        with pytest.raises(TrainValidationError):
            await use_case.execute("123")  # Too short

    @pytest.mark.asyncio
    async def test_train_not_found(self, use_case):
        """Test when train doesn't exist."""
        with pytest.raises(TrainNotFoundError):
            await use_case.execute("99999")


class TestSearchTrainsUseCase:
    """Test suite for train search use case."""

    @pytest.fixture
    def mock_repository(self):
        return MockTrainRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        return SearchTrainsUseCase(train_repository=mock_repository)

    @pytest.mark.asyncio
    async def test_search_success(self, use_case):
        """Test successful train search."""
        result = await use_case.execute("NDLS", "HWH")

        assert result.success is True
        assert result.from_station == "NDLS"
        assert result.to_station == "HWH"
        assert result.trains_found >= 1

    @pytest.mark.asyncio
    async def test_search_no_results(self, use_case):
        """Test search with no matching trains."""
        result = await use_case.execute("ABC", "XYZ")

        assert result.success is True
        assert result.trains_found == 0
        assert result.trains == []

    @pytest.mark.asyncio
    async def test_same_station_error(self, use_case):
        """Test that same source and destination raises error."""
        with pytest.raises(StationValidationError) as exc_info:
            await use_case.execute("NDLS", "NDLS")

        assert "cannot be same" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_station_code(self, use_case):
        """Test validation for invalid station codes."""
        with pytest.raises(StationValidationError):
            await use_case.execute("A", "B")  # Too short

    @pytest.mark.asyncio
    async def test_case_insensitive(self, use_case):
        """Test that station codes are case-insensitive."""
        result = await use_case.execute("ndls", "hwh")

        assert result.from_station == "NDLS"
        assert result.to_station == "HWH"
