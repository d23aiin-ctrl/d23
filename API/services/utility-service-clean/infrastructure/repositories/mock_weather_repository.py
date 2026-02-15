"""Mock Weather Repository Implementation."""
from typing import Optional
from datetime import datetime
from domain.entities import Weather, WeatherForecast
from domain.repositories import WeatherRepository


class MockWeatherRepository(WeatherRepository):
    """Mock implementation of weather repository for testing."""

    def __init__(self):
        self._weather_data = {
            "delhi": Weather(
                city="Delhi",
                temperature=32.5,
                feels_like=35.0,
                humidity=65,
                description="Partly Cloudy",
                wind_speed=12.5,
                pressure=1012,
                visibility=8000,
                icon="02d",
                timestamp=datetime.now()
            ),
            "mumbai": Weather(
                city="Mumbai",
                temperature=30.0,
                feels_like=33.5,
                humidity=80,
                description="Humid",
                wind_speed=18.0,
                pressure=1008,
                visibility=6000,
                icon="03d",
                timestamp=datetime.now()
            ),
            "bangalore": Weather(
                city="Bangalore",
                temperature=25.0,
                feels_like=26.5,
                humidity=55,
                description="Clear Sky",
                wind_speed=8.0,
                pressure=1015,
                visibility=10000,
                icon="01d",
                timestamp=datetime.now()
            ),
        }

    async def get_current_weather(self, city: str) -> Optional[Weather]:
        return self._weather_data.get(city.lower())

    async def get_forecast(self, city: str, days: int = 5) -> Optional[WeatherForecast]:
        weather = self._weather_data.get(city.lower())
        if not weather:
            return None
        return WeatherForecast(
            city=weather.city,
            forecasts=[weather] * days,
            updated_at=datetime.now()
        )
