"""Fuel Price DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class FuelTypeDTO(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"


class FuelPriceRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)
    fuel_type: Optional[FuelTypeDTO] = None


class FuelPriceDTO(BaseModel):
    fuel_type: str
    price: float
    city: str
    state: str
    change: float = 0


class FuelPriceResponse(BaseModel):
    success: bool = True
    data: Optional[List[FuelPriceDTO]] = None
    error: Optional[str] = None
