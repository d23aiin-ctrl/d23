"""
Driving License Domain Entities.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from enum import Enum


class VehicleClass(Enum):
    """Vehicle class codes."""
    MCWG = ("MCWG", "Motor Cycle With Gear")
    MCWOG = ("MCWOG", "Motor Cycle Without Gear")
    LMV = ("LMV", "Light Motor Vehicle")
    LMV_NT = ("LMV-NT", "Light Motor Vehicle Non-Transport")
    HMV = ("HMV", "Heavy Motor Vehicle")
    HGMV = ("HGMV", "Heavy Goods Motor Vehicle")
    HPMV = ("HPMV", "Heavy Passenger Motor Vehicle")
    TRANS = ("TRANS", "Transport")

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description


class DLStatus(Enum):
    """Driving license status."""
    ACTIVE = "Active"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"
    REVOKED = "Revoked"


@dataclass
class DrivingLicense:
    """
    Driving License entity.

    Contains DL details and validity information.
    """
    dl_number: str
    name: str
    father_name: str
    date_of_birth: date
    blood_group: Optional[str]
    address: str
    state: str
    rto_code: str

    # Validity
    issue_date: date
    validity_nt: date  # Non-transport validity
    validity_trans: Optional[date] = None  # Transport validity

    # Vehicle classes
    vehicle_classes: List[VehicleClass] = field(default_factory=list)

    # Status
    status: DLStatus = DLStatus.ACTIVE

    # Additional
    photo_url: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if DL is currently valid."""
        if self.status != DLStatus.ACTIVE:
            return False
        today = date.today()
        return self.validity_nt >= today

    @property
    def days_to_expiry(self) -> int:
        """Days until expiry."""
        return (self.validity_nt - date.today()).days

    @property
    def is_expiring_soon(self) -> bool:
        """Check if expiring within 30 days."""
        return 0 < self.days_to_expiry <= 30

    def has_class(self, vehicle_class: VehicleClass) -> bool:
        """Check if DL has specific vehicle class."""
        return vehicle_class in self.vehicle_classes

    def validate(self) -> List[str]:
        """Validate DL data."""
        errors = []
        if not self.dl_number:
            errors.append("DL number required")
        if len(self.dl_number) < 10:
            errors.append("Invalid DL number format")
        if not self.vehicle_classes:
            errors.append("At least one vehicle class required")
        return errors
