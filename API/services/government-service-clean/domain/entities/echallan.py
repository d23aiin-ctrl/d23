"""
E-Challan Domain Entities.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class ViolationType(Enum):
    """Traffic violation types."""
    OVERSPEEDING = ("Overspeeding", 1000)
    SIGNAL_JUMP = ("Signal Jump", 1000)
    NO_HELMET = ("No Helmet", 500)
    NO_SEATBELT = ("No Seatbelt", 500)
    WRONG_PARKING = ("Wrong Parking", 500)
    NO_LICENSE = ("Driving Without License", 5000)
    NO_INSURANCE = ("No Insurance", 2000)
    DRUNK_DRIVING = ("Drunk Driving", 10000)
    OVERLOADING = ("Overloading", 2000)
    NO_PUCC = ("No Pollution Certificate", 500)
    USING_PHONE = ("Using Phone While Driving", 1500)
    DANGEROUS_DRIVING = ("Dangerous Driving", 5000)

    def __init__(self, description: str, base_fine: int):
        self.description = description
        self.base_fine = base_fine


class ChallanStatus(Enum):
    """Challan payment status."""
    PENDING = "Pending"
    PAID = "Paid"
    DISPUTED = "Disputed"
    COURT = "Under Court"
    WAIVED = "Waived"


@dataclass
class Violation:
    """Single violation in a challan."""
    violation_type: ViolationType
    fine_amount: float
    description: Optional[str] = None


@dataclass
class EChallan:
    """
    E-Challan (Traffic Fine) entity.
    """
    challan_number: str
    challan_date: datetime
    vehicle_number: str

    # Location
    location: str
    city: str
    state: str

    # Violations
    violations: List[Violation] = field(default_factory=list)

    # Officer
    officer_id: Optional[str] = None
    officer_name: Optional[str] = None

    # Payment
    status: ChallanStatus = ChallanStatus.PENDING
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None

    # Due date
    due_date: Optional[date] = None

    # Evidence
    image_url: Optional[str] = None

    @property
    def total_fine(self) -> float:
        """Total fine amount."""
        return sum(v.fine_amount for v in self.violations)

    @property
    def is_paid(self) -> bool:
        """Check if challan is paid."""
        return self.status == ChallanStatus.PAID

    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue."""
        if self.is_paid or not self.due_date:
            return False
        return date.today() > self.due_date

    @property
    def days_overdue(self) -> int:
        """Days since due date."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    def validate(self) -> List[str]:
        """Validate challan data."""
        errors = []
        if not self.challan_number:
            errors.append("Challan number required")
        if not self.vehicle_number:
            errors.append("Vehicle number required")
        if not self.violations:
            errors.append("At least one violation required")
        return errors
