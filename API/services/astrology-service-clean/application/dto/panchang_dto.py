"""
Panchang DTOs.

API request/response models for Hindu calendar endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PanchangRequest(BaseModel):
    """Panchang request."""
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD), default today")
    city: str = Field(default="Delhi")
    latitude: float = Field(default=28.6139)
    longitude: float = Field(default=77.2090)


class TithiDTO(BaseModel):
    """Tithi details."""
    number: int
    name: str
    name_hindi: str
    paksha: str  # Shukla/Krishna
    end_time: str
    is_auspicious: bool


class MuhurtaDTO(BaseModel):
    """Muhurta (time period)."""
    name: str
    start_time: str
    end_time: str
    is_auspicious: bool
    suitable_for: List[str] = []


class PanchangResponse(BaseModel):
    """Panchang response."""
    success: bool = True
    date: str
    day: str
    day_hindi: str

    # Location
    city: str

    # Hindu calendar
    hindu_month: str
    hindu_month_hindi: str
    hindu_year: int

    # Five limbs (Panch-Ang)
    tithi: TithiDTO
    nakshatra: str
    nakshatra_hindi: str
    nakshatra_end_time: str
    yoga: str
    yoga_hindi: str
    yoga_end_time: str
    karana: str
    karana_hindi: str

    # Sun/Moon times
    sunrise: str
    sunset: str
    moonrise: Optional[str] = None
    moonset: Optional[str] = None

    # Muhurtas
    abhijit_muhurta: Optional[MuhurtaDTO] = None
    rahukaal: Optional[MuhurtaDTO] = None
    yamaganda: Optional[MuhurtaDTO] = None

    # Special occasions
    is_auspicious_day: bool
    is_ekadashi: bool = False
    is_pradosh: bool = False
    is_amavasya: bool = False
    is_purnima: bool = False
    festivals: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "date": "2026-02-04",
                "day": "Wednesday",
                "day_hindi": "बुधवार",
                "city": "Delhi",
                "hindu_month": "Magha",
                "hindu_month_hindi": "माघ",
                "hindu_year": 2082,
                "tithi": {
                    "number": 7,
                    "name": "Saptami",
                    "name_hindi": "सप्तमी",
                    "paksha": "Shukla",
                    "end_time": "18:45",
                    "is_auspicious": True
                },
                "nakshatra": "Ashwini",
                "nakshatra_hindi": "अश्विनी",
                "sunrise": "06:58",
                "sunset": "18:05"
            }
        }
