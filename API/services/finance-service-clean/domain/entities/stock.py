"""Stock Domain Entities."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum

class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"

@dataclass
class StockPrice:
    symbol: str
    name: str
    exchange: Exchange
    price: float
    change: float
    change_percent: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    timestamp: Optional[datetime] = None

@dataclass
class Stock:
    symbol: str
    name: str
    sector: str
    exchange: Exchange
