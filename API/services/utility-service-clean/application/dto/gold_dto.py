"""Gold Price DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class MetalTypeDTO(str, Enum):
    GOLD_24K = "gold_24k"
    GOLD_22K = "gold_22k"
    GOLD_18K = "gold_18k"
    SILVER = "silver"


class GoldPriceRequest(BaseModel):
    metal_type: Optional[MetalTypeDTO] = None
    city: str = "Delhi"


class GoldPriceDTO(BaseModel):
    metal_type: str
    price_per_gram: float
    price_per_10gram: float
    city: str
    change: float = 0
    change_percent: float = 0


class GoldPriceResponse(BaseModel):
    success: bool = True
    data: Optional[List[GoldPriceDTO]] = None
    error: Optional[str] = None
