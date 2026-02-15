"""
Horoscope DTOs.

API request/response models for horoscope endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class LuckyElementsDTO(BaseModel):
    """Lucky elements response."""
    numbers: List[int]
    colors: List[str]
    time: str
    day: str


class HoroscopeRequest(BaseModel):
    """Horoscope request model."""
    sign: str = Field(..., description="Zodiac sign (English or Hindi)")
    period: str = Field(default="daily", description="daily/weekly/monthly")
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")


class HoroscopeResponse(BaseModel):
    """Horoscope response model."""
    success: bool = True
    sign: str
    sign_hindi: str
    period: str
    date: str

    # Main prediction
    prediction: str

    # Scores (0-100)
    overall_score: int
    love_score: int
    career_score: int
    health_score: int
    finance_score: int

    # Detailed predictions
    love_prediction: Optional[str] = None
    career_prediction: Optional[str] = None
    health_prediction: Optional[str] = None
    finance_prediction: Optional[str] = None

    # Additional info
    mood: Optional[str] = None
    health_tip: Optional[str] = None
    lucky: Optional[LuckyElementsDTO] = None
    compatible_signs: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "sign": "Aries",
                "sign_hindi": "मेष",
                "period": "daily",
                "date": "2026-02-04",
                "prediction": "Today brings positive energy...",
                "overall_score": 75,
                "love_score": 80,
                "career_score": 70,
                "health_score": 75,
                "finance_score": 75,
                "mood": "Optimistic",
                "lucky": {
                    "numbers": [3, 7, 9],
                    "colors": ["Red", "Orange"],
                    "time": "2:00 PM - 4:00 PM",
                    "day": "Tuesday"
                }
            }
        }
