"""
Vehicle RC Domain Entities.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import date
from enum import Enum


class FuelType(Enum):
    """Vehicle fuel types."""
    PETROL = "Petrol"
    DIESEL = "Diesel"
    CNG = "CNG"
    LPG = "LPG"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"


class VehicleType(Enum):
    """Vehicle types."""
    TWO_WHEELER = "Two Wheeler"
    THREE_WHEELER = "Three Wheeler"
    FOUR_WHEELER = "Four Wheeler"
    COMMERCIAL = "Commercial"


@dataclass
class VehicleOwner:
    """Vehicle owner details."""
    name: str
    father_name: str
    address: str
    mobile: Optional[str] = None


@dataclass
class VehicleRC:
    """
    Vehicle Registration Certificate (RC) entity.
    """
    registration_number: str
    registration_date: date
    rto_code: str
    rto_name: str
    state: str

    # Vehicle details
    make: str  # Manufacturer
    model: str
    vehicle_type: VehicleType
    fuel_type: FuelType
    color: str

    # Technical details
    engine_number: str
    chassis_number: str
    cubic_capacity: int  # CC
    seating_capacity: int
    gross_weight: Optional[int] = None

    # Owner
    owner: Optional[VehicleOwner] = None

    # Validity
    fitness_upto: Optional[date] = None
    tax_upto: Optional[date] = None
    insurance_upto: Optional[date] = None
    pucc_upto: Optional[date] = None  # Pollution certificate

    # Status
    is_financed: bool = False
    financer_name: Optional[str] = None
    is_blacklisted: bool = False

    @property
    def is_tax_valid(self) -> bool:
        """Check if road tax is valid."""
        if not self.tax_upto:
            return False
        return self.tax_upto >= date.today()

    @property
    def is_insurance_valid(self) -> bool:
        """Check if insurance is valid."""
        if not self.insurance_upto:
            return False
        return self.insurance_upto >= date.today()

    @property
    def is_fitness_valid(self) -> bool:
        """Check if fitness certificate is valid."""
        if not self.fitness_upto:
            return True  # Not all vehicles need fitness
        return self.fitness_upto >= date.today()

    @property
    def pending_documents(self) -> List[str]:
        """List of expired/missing documents."""
        pending = []
        if not self.is_tax_valid:
            pending.append("Road Tax")
        if not self.is_insurance_valid:
            pending.append("Insurance")
        if not self.is_fitness_valid:
            pending.append("Fitness Certificate")
        if self.pucc_upto and self.pucc_upto < date.today():
            pending.append("PUCC")
        return pending

    def validate(self) -> List[str]:
        """Validate RC data."""
        errors = []
        if not self.registration_number:
            errors.append("Registration number required")
        if not self.engine_number:
            errors.append("Engine number required")
        if not self.chassis_number:
            errors.append("Chassis number required")
        return errors
