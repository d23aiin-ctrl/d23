"""Holiday Domain Entities."""
from dataclasses import dataclass
from enum import Enum
from datetime import date
from typing import Optional


class HolidayType(Enum):
    NATIONAL = "national"
    REGIONAL = "regional"
    BANK = "bank"
    OPTIONAL = "optional"


@dataclass
class Holiday:
    name: str
    date: date
    holiday_type: HolidayType
    day: str  # Monday, Tuesday, etc.
    description: Optional[str] = None
    state: Optional[str] = None  # For regional holidays
