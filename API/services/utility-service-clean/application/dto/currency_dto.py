"""Currency DTOs."""
from pydantic import BaseModel, Field
from typing import Optional


class CurrencyRequest(BaseModel):
    base: str = Field("USD", min_length=3, max_length=3)
    quote: str = Field("INR", min_length=3, max_length=3)


class ConversionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)


class CurrencyRateDTO(BaseModel):
    base: str
    quote: str
    rate: float
    change: float = 0
    change_percent: float = 0


class CurrencyResponse(BaseModel):
    success: bool = True
    data: Optional[CurrencyRateDTO] = None
    error: Optional[str] = None


class ConversionResponse(BaseModel):
    success: bool = True
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    rate: float
