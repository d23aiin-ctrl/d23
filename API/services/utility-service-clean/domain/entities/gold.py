"""Gold Price Domain Entities."""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class MetalType(Enum):
    GOLD_24K = "gold_24k"
    GOLD_22K = "gold_22k"
    GOLD_18K = "gold_18k"
    SILVER = "silver"


@dataclass
class GoldPrice:
    metal_type: MetalType
    price_per_gram: float
    price_per_10gram: float
    city: str
    change: float = 0
    change_percent: float = 0
    timestamp: Optional[datetime] = None
