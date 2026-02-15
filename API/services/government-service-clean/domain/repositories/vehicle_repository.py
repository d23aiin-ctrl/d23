"""Vehicle Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import VehicleRC


class VehicleRepository(ABC):
    """Abstract repository for vehicle operations."""

    @abstractmethod
    async def get_by_registration(self, registration_number: str) -> Optional[VehicleRC]:
        """Get vehicle by registration number."""
        pass

    @abstractmethod
    async def get_by_chassis(self, chassis_number: str) -> Optional[VehicleRC]:
        """Get vehicle by chassis number."""
        pass
