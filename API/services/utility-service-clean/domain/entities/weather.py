"""Weather Domain Entities."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Weather:
    city: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    pressure: int
    visibility: int
    icon: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class WeatherForecast:
    city: str
    forecasts: list  # List of Weather objects
    updated_at: Optional[datetime] = None
