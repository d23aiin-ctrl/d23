"""Pincode Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import PincodeInfo


class PincodeRepository(ABC):
    """Abstract repository for pincode lookup."""

    @abstractmethod
    async def get_by_pincode(self, pincode: str) -> List[PincodeInfo]:
        """Get location info by pincode."""
        pass

    @abstractmethod
    async def search_by_area(self, area: str, state: Optional[str] = None) -> List[PincodeInfo]:
        """Search pincodes by area name."""
        pass
