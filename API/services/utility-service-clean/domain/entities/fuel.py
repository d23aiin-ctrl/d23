"""Fuel Price Domain Entities."""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class FuelType(Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"


@dataclass
class FuelPrice:
    fuel_type: FuelType
    price: float
    city: str
    state: str
    change: float = 0
    effective_date: Optional[datetime] = None
