"""Domain Repository Interfaces."""

from .pmkisan_repository import PMKisanRepository
from .dl_repository import DLRepository
from .vehicle_repository import VehicleRepository
from .echallan_repository import EChallanRepository

__all__ = [
    "PMKisanRepository",
    "DLRepository",
    "VehicleRepository",
    "EChallanRepository",
]
