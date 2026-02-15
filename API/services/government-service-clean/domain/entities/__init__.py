"""
Domain Entities for Government Service.

Core business objects for government services.
"""

from .pmkisan import PMKisanBeneficiary, PMKisanInstallment, InstallmentStatus
from .driving_license import DrivingLicense, VehicleClass, DLStatus
from .vehicle import VehicleRC, VehicleOwner, FuelType, VehicleType
from .echallan import EChallan, Violation, ViolationType, ChallanStatus

__all__ = [
    "PMKisanBeneficiary",
    "PMKisanInstallment",
    "InstallmentStatus",
    "DrivingLicense",
    "VehicleClass",
    "DLStatus",
    "VehicleRC",
    "VehicleOwner",
    "FuelType",
    "VehicleType",
    "EChallan",
    "Violation",
    "ViolationType",
    "ChallanStatus",
]
