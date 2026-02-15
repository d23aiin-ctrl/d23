"""Currency Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import CurrencyRate, CurrencyPair


class CurrencyRepository(ABC):
    """Abstract repository for currency rates."""

    @abstractmethod
    async def get_rate(self, base: str, quote: str) -> Optional[CurrencyRate]:
        """Get exchange rate for currency pair."""
        pass

    @abstractmethod
    async def get_rates_for_base(self, base: str) -> List[CurrencyRate]:
        """Get all rates for a base currency."""
        pass

    @abstractmethod
    async def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies."""
        pass
