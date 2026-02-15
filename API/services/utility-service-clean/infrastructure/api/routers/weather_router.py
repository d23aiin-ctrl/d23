"""Weather API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import WeatherRequest, WeatherResponse
from application.use_cases import GetWeatherUseCase
from application.use_cases.get_weather import WeatherNotFoundError
from infrastructure.api.dependencies import get_weather_use_case

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/{city}", response_model=WeatherResponse)
async def get_weather(
    city: str,
    use_case: GetWeatherUseCase = Depends(get_weather_use_case)
) -> WeatherResponse:
    """Get current weather for city."""
    try:
        request = WeatherRequest(city=city)
        return await use_case.execute(request)
    except WeatherNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
