"""Fuel Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import FuelPrice, FuelType


class FuelRepository(ABC):
    """Abstract repository for fuel prices."""

    @abstractmethod
    async def get_price(self, fuel_type: FuelType, city: str) -> Optional[FuelPrice]:
        """Get fuel price for city."""
        pass

    @abstractmethod
    async def get_all_prices(self, city: str) -> List[FuelPrice]:
        """Get all fuel prices for city."""
        pass
