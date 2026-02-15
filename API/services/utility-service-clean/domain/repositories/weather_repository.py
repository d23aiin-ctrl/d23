"""Weather Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import Weather, WeatherForecast


class WeatherRepository(ABC):
    """Abstract repository for weather data."""

    @abstractmethod
    async def get_current_weather(self, city: str) -> Optional[Weather]:
        """Get current weather for city."""
        pass

    @abstractmethod
    async def get_forecast(self, city: str, days: int = 5) -> Optional[WeatherForecast]:
        """Get weather forecast for city."""
        pass
