"""Mock Currency Repository Implementation."""
from typing import List, Optional
from datetime import datetime
from domain.entities import CurrencyRate, CurrencyPair
from domain.repositories import CurrencyRepository


class MockCurrencyRepository(CurrencyRepository):
    """Mock implementation of currency repository for testing."""

    def __init__(self):
        self._rates = {
            ("USD", "INR"): 83.12,
            ("EUR", "INR"): 89.45,
            ("GBP", "INR"): 104.78,
            ("AED", "INR"): 22.64,
            ("JPY", "INR"): 0.55,
            ("INR", "USD"): 0.012,
        }

    async def get_rate(self, base: str, quote: str) -> Optional[CurrencyRate]:
        rate = self._rates.get((base.upper(), quote.upper()))
        if not rate:
            return None
        return CurrencyRate(
            pair=CurrencyPair(base=base.upper(), quote=quote.upper()),
            rate=rate,
            change=0.15,
            change_percent=0.18,
            timestamp=datetime.now()
        )

    async def get_rates_for_base(self, base: str) -> List[CurrencyRate]:
        rates = []
        for (b, q), rate in self._rates.items():
            if b == base.upper():
                rates.append(CurrencyRate(
                    pair=CurrencyPair(base=b, quote=q),
                    rate=rate,
                    timestamp=datetime.now()
                ))
        return rates

    async def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        rate = self._rates.get((from_currency.upper(), to_currency.upper()))
        if not rate:
            return 0.0
        return amount * rate
