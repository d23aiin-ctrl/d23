"""Currency Domain Entities."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CurrencyPair:
    base: str
    quote: str

    def __str__(self):
        return f"{self.base}/{self.quote}"


@dataclass
class CurrencyRate:
    pair: CurrencyPair
    rate: float
    change: float = 0
    change_percent: float = 0
    timestamp: Optional[datetime] = None
