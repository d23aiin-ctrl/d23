"""
Unit Tests for GetPNRStatusUseCase.

These tests demonstrate how Clean Architecture enables testing:
- Use cases are tested with mock repositories
- No HTTP, no database, no external APIs
- Fast, isolated, reliable tests
"""

import pytest
from datetime import date

from domain.entities import PNR, Passenger, BookingStatus
from application.use_cases import GetPNRStatusUseCase
from application.use_cases.get_pnr_status import PNRValidationError, PNRNotFoundError
from infrastructure.repositories import MockPNRRepository


class TestGetPNRStatusUseCase:
    """Test suite for PNR status use case."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        return MockPNRRepository()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mock repository."""
        return GetPNRStatusUseCase(pnr_repository=mock_repository)

    # =========================================================================
    # Success Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_pnr_success(self, use_case):
        """Test successful PNR lookup."""
        # The mock repository has PNR "1234567890" pre-loaded
        result = await use_case.execute("1234567890")

        assert result.success is True
        assert result.pnr == "1234567890"
        assert result.train_number == "12301"
        assert result.train_name == "Howrah Rajdhani Express"
        assert len(result.passengers) == 2
        assert result.all_confirmed is True

    @pytest.mark.asyncio
    async def test_pnr_with_partial_confirmation(self, use_case, mock_repository):
        """Test PNR where some passengers are waitlisted."""
        # Add a custom PNR with mixed status
        custom_pnr = PNR(
            pnr_number="1111111111",
            train_number="12302",
            train_name="Test Express",
            journey_date=date(2026, 3, 1),
            from_station_code="NDLS",
            from_station_name="New Delhi",
            to_station_code="HWH",
            to_station_name="Howrah",
            travel_class="SL",
            passengers=[
                Passenger(1, BookingStatus.WAITLIST, BookingStatus.CONFIRMED, "S1", 10, "LB"),
                Passenger(2, BookingStatus.WAITLIST, BookingStatus.WAITLIST),  # Still waitlisted
            ],
            chart_prepared=False,
        )
        mock_repository.add_pnr(custom_pnr)

        result = await use_case.execute("1111111111")

        assert result.success is True
        assert result.total_passengers == 2
        assert result.confirmed_passengers == 1
        assert result.all_confirmed is False
        assert "1/2" in result.status_summary

    # =========================================================================
    # Validation Error Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_invalid_pnr_length(self, use_case):
        """Test that short PNR raises validation error."""
        with pytest.raises(PNRValidationError) as exc_info:
            await use_case.execute("12345")

        assert "10 digits" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_pnr_characters(self, use_case):
        """Test that non-numeric PNR raises validation error."""
        with pytest.raises(PNRValidationError) as exc_info:
            await use_case.execute("123456789A")

        assert "only digits" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_pnr(self, use_case):
        """Test that empty PNR raises validation error."""
        with pytest.raises(PNRValidationError) as exc_info:
            await use_case.execute("")

        assert "required" in str(exc_info.value)

    # =========================================================================
    # Not Found Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_pnr_not_found(self, use_case):
        """Test that non-existent PNR raises not found error."""
        with pytest.raises(PNRNotFoundError) as exc_info:
            await use_case.execute("9999999999")

        assert "not found" in str(exc_info.value)


class TestPNREntity:
    """Test PNR domain entity business logic."""

    def test_all_confirmed(self):
        """Test all_confirmed property."""
        pnr = PNR(
            pnr_number="1234567890",
            train_number="12301",
            train_name="Test",
            journey_date=date.today(),
            from_station_code="A",
            from_station_name="Station A",
            to_station_code="B",
            to_station_name="Station B",
            travel_class="3A",
            passengers=[
                Passenger(1, BookingStatus.CONFIRMED, BookingStatus.CONFIRMED),
                Passenger(2, BookingStatus.CONFIRMED, BookingStatus.CONFIRMED),
            ]
        )

        assert pnr.all_confirmed is True
        assert pnr.confirmed_passengers == 2

    def test_partial_confirmation(self):
        """Test partial confirmation detection."""
        pnr = PNR(
            pnr_number="1234567890",
            train_number="12301",
            train_name="Test",
            journey_date=date.today(),
            from_station_code="A",
            from_station_name="Station A",
            to_station_code="B",
            to_station_name="Station B",
            travel_class="3A",
            passengers=[
                Passenger(1, BookingStatus.CONFIRMED, BookingStatus.CONFIRMED),
                Passenger(2, BookingStatus.WAITLIST, BookingStatus.WAITLIST),
            ]
        )

        assert pnr.all_confirmed is False
        assert pnr.confirmed_passengers == 1
        assert pnr.total_passengers == 2

    def test_validation(self):
        """Test PNR validation."""
        # Invalid PNR
        pnr = PNR(
            pnr_number="12345",  # Too short
            train_number="12301",
            train_name="Test",
            journey_date=date.today(),
            from_station_code="A",
            from_station_name="Station A",
            to_station_code="B",
            to_station_name="Station B",
            travel_class="3A",
            passengers=[]  # No passengers
        )

        errors = pnr.validate()
        assert len(errors) == 2
        assert any("10 digits" in e for e in errors)
        assert any("at least one passenger" in e for e in errors)


class TestPassengerEntity:
    """Test Passenger domain entity."""

    def test_status_improved(self):
        """Test status improvement detection."""
        passenger = Passenger(
            number=1,
            booking_status=BookingStatus.WAITLIST,
            current_status=BookingStatus.CONFIRMED,
        )

        assert passenger.is_confirmed is True
        assert passenger.status_improved is True

    def test_status_not_improved(self):
        """Test when status hasn't improved."""
        passenger = Passenger(
            number=1,
            booking_status=BookingStatus.WAITLIST,
            current_status=BookingStatus.WAITLIST,
        )

        assert passenger.is_confirmed is False
        assert passenger.status_improved is False
