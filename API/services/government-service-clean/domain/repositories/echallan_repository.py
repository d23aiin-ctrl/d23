"""E-Challan Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities import EChallan


class EChallanRepository(ABC):
    """Abstract repository for e-challan operations."""

    @abstractmethod
    async def get_by_vehicle(self, vehicle_number: str) -> List[EChallan]:
        """Get all challans for a vehicle."""
        pass

    @abstractmethod
    async def get_by_challan_number(self, challan_number: str) -> Optional[EChallan]:
        """Get challan by number."""
        pass

    @abstractmethod
    async def get_pending(self, vehicle_number: str) -> List[EChallan]:
        """Get pending (unpaid) challans for a vehicle."""
        pass
