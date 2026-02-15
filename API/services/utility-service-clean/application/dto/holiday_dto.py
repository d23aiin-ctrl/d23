"""Holiday DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class HolidayTypeDTO(str, Enum):
    NATIONAL = "national"
    REGIONAL = "regional"
    BANK = "bank"
    OPTIONAL = "optional"


class HolidayRequest(BaseModel):
    year: int = Field(default=2024, ge=2020, le=2030)
    state: Optional[str] = None
    holiday_type: Optional[HolidayTypeDTO] = None


class HolidayDTO(BaseModel):
    name: str
    date: date
    holiday_type: str
    day: str
    description: Optional[str] = None
    state: Optional[str] = None


class HolidayResponse(BaseModel):
    success: bool = True
    data: Optional[List[HolidayDTO]] = None
    error: Optional[str] = None
