"""Stock DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExchangeDTO(str, Enum):
    NSE = "NSE"
    BSE = "BSE"


class StockPriceRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: ExchangeDTO = ExchangeDTO.NSE


class StockSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50)


class StockDTO(BaseModel):
    symbol: str
    name: str
    sector: str
    exchange: str


class StockPriceDTO(BaseModel):
    symbol: str
    name: str
    exchange: str
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


class StockPriceResponse(BaseModel):
    success: bool = True
    data: Optional[StockPriceDTO] = None
    error: Optional[str] = None


class StockSearchResponse(BaseModel):
    success: bool = True
    results: List[StockDTO] = []


class TopMoversResponse(BaseModel):
    success: bool = True
    gainers: List[StockPriceDTO] = []
    losers: List[StockPriceDTO] = []
