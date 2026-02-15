"""Fuel Price API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import FuelPriceRequest, FuelPriceResponse
from application.use_cases import GetFuelPriceUseCase
from application.use_cases.get_fuel_price import FuelPriceNotFoundError
from infrastructure.api.dependencies import get_fuel_price_use_case

router = APIRouter(prefix="/fuel", tags=["Fuel Prices"])


@router.get("/{city}", response_model=FuelPriceResponse)
async def get_fuel_prices(
    city: str,
    use_case: GetFuelPriceUseCase = Depends(get_fuel_price_use_case)
) -> FuelPriceResponse:
    """Get fuel prices for city."""
    try:
        request = FuelPriceRequest(city=city)
        return await use_case.execute(request)
    except FuelPriceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
