"""Get Fuel Price Use Case."""
from domain.repositories import FuelRepository
from application.dto import FuelPriceRequest, FuelPriceResponse
from application.dto.fuel_dto import FuelPriceDTO


class FuelPriceNotFoundError(Exception):
    """Raised when fuel price data is not available."""
    pass


class GetFuelPriceUseCase:
    """Use case for getting fuel prices."""

    def __init__(self, fuel_repository: FuelRepository):
        self.fuel_repository = fuel_repository

    async def execute(self, request: FuelPriceRequest) -> FuelPriceResponse:
        """Get fuel prices for city."""
        prices = await self.fuel_repository.get_all_prices(request.city)

        if not prices:
            raise FuelPriceNotFoundError(f"Fuel prices not available for {request.city}")

        return FuelPriceResponse(
            success=True,
            data=[
                FuelPriceDTO(
                    fuel_type=p.fuel_type.value,
                    price=p.price,
                    city=p.city,
                    state=p.state,
                    change=p.change
                )
                for p in prices
            ]
        )
