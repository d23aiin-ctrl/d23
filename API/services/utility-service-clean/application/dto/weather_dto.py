"""Weather DTOs."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)


class WeatherDTO(BaseModel):
    city: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    pressure: int
    visibility: int
    icon: Optional[str] = None


class WeatherResponse(BaseModel):
    success: bool = True
    data: Optional[WeatherDTO] = None
    error: Optional[str] = None
