"""
PNR Domain Entity.

Represents a railway ticket booking with passengers.
This is a pure domain object with business logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import date


class BookingStatus(Enum):
    """Booking status enumeration."""
    CONFIRMED = "CNF"
    WAITLIST = "WL"
    RAC = "RAC"
    CANCELLED = "CAN"

    @classmethod
    def from_string(cls, status: str) -> "BookingStatus":
        """Parse status from string like 'CNF', 'W/L 5', 'RAC 10'."""
        status_upper = status.upper()
        if "CNF" in status_upper or "CONFIRM" in status_upper:
            return cls.CONFIRMED
        elif "W/L" in status_upper or "WL" in status_upper:
            return cls.WAITLIST
        elif "RAC" in status_upper:
            return cls.RAC
        elif "CAN" in status_upper:
            return cls.CANCELLED
        return cls.WAITLIST


@dataclass
class Passenger:
    """Individual passenger in a booking."""
    number: int
    booking_status: BookingStatus
    current_status: BookingStatus
    coach: Optional[str] = None
    berth: Optional[int] = None
    berth_type: Optional[str] = None  # LB, UB, MB, SL, SU

    @property
    def is_confirmed(self) -> bool:
        """Check if passenger is confirmed."""
        return self.current_status == BookingStatus.CONFIRMED

    @property
    def status_improved(self) -> bool:
        """Check if status improved from booking."""
        status_rank = {
            BookingStatus.CANCELLED: 0,
            BookingStatus.WAITLIST: 1,
            BookingStatus.RAC: 2,
            BookingStatus.CONFIRMED: 3,
        }
        return status_rank[self.current_status] > status_rank[self.booking_status]


@dataclass
class PNR:
    """
    PNR (Passenger Name Record) entity.

    Represents a complete railway booking with all passengers.
    Contains business logic for booking status.
    """
    pnr_number: str
    train_number: str
    train_name: str
    journey_date: date
    from_station_code: str
    from_station_name: str
    to_station_code: str
    to_station_name: str
    travel_class: str  # SL, 3A, 2A, 1A
    passengers: List[Passenger] = field(default_factory=list)
    chart_prepared: bool = False
    booking_fare: Optional[float] = None

    @property
    def total_passengers(self) -> int:
        """Total number of passengers."""
        return len(self.passengers)

    @property
    def confirmed_passengers(self) -> int:
        """Count of confirmed passengers."""
        return sum(1 for p in self.passengers if p.is_confirmed)

    @property
    def all_confirmed(self) -> bool:
        """Check if all passengers are confirmed."""
        return all(p.is_confirmed for p in self.passengers)

    @property
    def booking_status_summary(self) -> str:
        """Get a summary of booking status."""
        if self.all_confirmed:
            return "All passengers confirmed"
        confirmed = self.confirmed_passengers
        total = self.total_passengers
        return f"{confirmed}/{total} passengers confirmed"

    def get_passenger(self, number: int) -> Optional[Passenger]:
        """Get passenger by number."""
        for p in self.passengers:
            if p.number == number:
                return p
        return None

    def validate(self) -> List[str]:
        """Validate PNR data, return list of errors."""
        errors = []
        if len(self.pnr_number) != 10:
            errors.append("PNR must be 10 digits")
        if not self.pnr_number.isdigit():
            errors.append("PNR must contain only digits")
        if not self.passengers:
            errors.append("PNR must have at least one passenger")
        return errors
