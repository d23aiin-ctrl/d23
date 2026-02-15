"""SIP Repository Interface."""
from abc import ABC, abstractmethod
from typing import List
from domain.entities import SIPCalculation


class SIPRepository(ABC):
    """Abstract repository for SIP calculations."""

    @abstractmethod
    async def save_calculation(self, calculation: SIPCalculation) -> str:
        """Save SIP calculation and return ID."""
        pass

    @abstractmethod
    async def get_calculation(self, calculation_id: str) -> SIPCalculation:
        """Retrieve saved calculation by ID."""
        pass

    @abstractmethod
    async def get_historical_returns(self, fund_type: str, years: int) -> List[float]:
        """Get historical return rates for fund type."""
        pass
