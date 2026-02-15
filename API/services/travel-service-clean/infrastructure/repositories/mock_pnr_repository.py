"""
Mock PNR Repository.

Used for testing and development.
Returns predefined test data.
"""

from typing import Optional
from datetime import date

from domain.repositories import PNRRepository
from domain.entities import PNR, Passenger, BookingStatus


class MockPNRRepository(PNRRepository):
    """
    Mock repository for testing.

    This allows testing use cases without external dependencies.
    """

    def __init__(self):
        # Predefined test data
        self._pnrs = {
            "1234567890": PNR(
                pnr_number="1234567890",
                train_number="12301",
                train_name="Howrah Rajdhani Express",
                journey_date=date(2026, 2, 15),
                from_station_code="NDLS",
                from_station_name="New Delhi",
                to_station_code="HWH",
                to_station_name="Howrah Junction",
                travel_class="3A",
                passengers=[
                    Passenger(
                        number=1,
                        booking_status=BookingStatus.WAITLIST,
                        current_status=BookingStatus.CONFIRMED,
                        coach="B2",
                        berth=25,
                        berth_type="LB"
                    ),
                    Passenger(
                        number=2,
                        booking_status=BookingStatus.WAITLIST,
                        current_status=BookingStatus.CONFIRMED,
                        coach="B2",
                        berth=26,
                        berth_type="MB"
                    ),
                ],
                chart_prepared=False,
                booking_fare=3500.00
            ),
            "9876543210": PNR(
                pnr_number="9876543210",
                train_number="12951",
                train_name="Mumbai Rajdhani Express",
                journey_date=date(2026, 2, 20),
                from_station_code="NDLS",
                from_station_name="New Delhi",
                to_station_code="BCT",
                to_station_name="Mumbai Central",
                travel_class="2A",
                passengers=[
                    Passenger(
                        number=1,
                        booking_status=BookingStatus.CONFIRMED,
                        current_status=BookingStatus.CONFIRMED,
                        coach="A1",
                        berth=15,
                        berth_type="LB"
                    ),
                ],
                chart_prepared=True,
                booking_fare=4500.00
            ),
        }

    async def get_by_pnr(self, pnr_number: str) -> Optional[PNR]:
        """Get PNR from mock data."""
        return self._pnrs.get(pnr_number)

    async def get_fare(
        self,
        train_number: str,
        from_station: str,
        to_station: str,
        travel_class: str
    ) -> Optional[float]:
        """Return mock fare."""
        # Simple mock calculation
        base_fares = {"SL": 500, "3A": 1500, "2A": 2500, "1A": 4000}
        return base_fares.get(travel_class, 1000)

    # Test helper methods
    def add_pnr(self, pnr: PNR) -> None:
        """Add a PNR for testing."""
        self._pnrs[pnr.pnr_number] = pnr

    def clear(self) -> None:
        """Clear all test data."""
        self._pnrs.clear()
