"""Get Weather Use Case."""
from domain.repositories import WeatherRepository
from application.dto import WeatherRequest, WeatherResponse
from application.dto.weather_dto import WeatherDTO


class WeatherNotFoundError(Exception):
    """Raised when weather data is not available."""
    pass


class GetWeatherUseCase:
    """Use case for getting weather data."""

    def __init__(self, weather_repository: WeatherRepository):
        self.weather_repository = weather_repository

    async def execute(self, request: WeatherRequest) -> WeatherResponse:
        """Get weather for city."""
        weather = await self.weather_repository.get_current_weather(request.city)

        if not weather:
            raise WeatherNotFoundError(f"Weather data not available for {request.city}")

        return WeatherResponse(
            success=True,
            data=WeatherDTO(
                city=weather.city,
                temperature=weather.temperature,
                feels_like=weather.feels_like,
                humidity=weather.humidity,
                description=weather.description,
                wind_speed=weather.wind_speed,
                pressure=weather.pressure,
                visibility=weather.visibility,
                icon=weather.icon
            )
        )
