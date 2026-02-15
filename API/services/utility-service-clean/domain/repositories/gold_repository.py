"""Gold Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import GoldPrice, MetalType


class GoldRepository(ABC):
    """Abstract repository for gold/silver prices."""

    @abstractmethod
    async def get_price(self, metal_type: MetalType, city: str = "Delhi") -> Optional[GoldPrice]:
        """Get current price for metal type in city."""
        pass

    @abstractmethod
    async def get_all_prices(self, city: str = "Delhi") -> List[GoldPrice]:
        """Get all metal prices for city."""
        pass
