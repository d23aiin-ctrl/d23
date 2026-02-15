"""Get Gold Price Use Case."""
from domain.repositories import GoldRepository
from application.dto import GoldPriceRequest, GoldPriceResponse
from application.dto.gold_dto import GoldPriceDTO


class GetGoldPriceUseCase:
    """Use case for getting gold/silver prices."""

    def __init__(self, gold_repository: GoldRepository):
        self.gold_repository = gold_repository

    async def execute(self, request: GoldPriceRequest) -> GoldPriceResponse:
        """Get gold/silver prices."""
        prices = await self.gold_repository.get_all_prices(request.city)

        return GoldPriceResponse(
            success=True,
            data=[
                GoldPriceDTO(
                    metal_type=p.metal_type.value,
                    price_per_gram=p.price_per_gram,
                    price_per_10gram=p.price_per_10gram,
                    city=p.city,
                    change=p.change,
                    change_percent=p.change_percent
                )
                for p in prices
            ]
        )
