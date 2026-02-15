"""Mock Gold Repository Implementation."""
from typing import List, Optional
from datetime import datetime
from domain.entities import GoldPrice, MetalType
from domain.repositories import GoldRepository


class MockGoldRepository(GoldRepository):
    """Mock implementation of gold repository for testing."""

    def __init__(self):
        self._prices = {
            MetalType.GOLD_24K: GoldPrice(
                metal_type=MetalType.GOLD_24K,
                price_per_gram=6250.0,
                price_per_10gram=62500.0,
                city="Delhi",
                change=50.0,
                change_percent=0.8,
                timestamp=datetime.now()
            ),
            MetalType.GOLD_22K: GoldPrice(
                metal_type=MetalType.GOLD_22K,
                price_per_gram=5730.0,
                price_per_10gram=57300.0,
                city="Delhi",
                change=45.0,
                change_percent=0.79,
                timestamp=datetime.now()
            ),
            MetalType.SILVER: GoldPrice(
                metal_type=MetalType.SILVER,
                price_per_gram=75.0,
                price_per_10gram=750.0,
                city="Delhi",
                change=-1.5,
                change_percent=-1.96,
                timestamp=datetime.now()
            ),
        }

    async def get_price(self, metal_type: MetalType, city: str = "Delhi") -> Optional[GoldPrice]:
        price = self._prices.get(metal_type)
        if price:
            price.city = city
        return price

    async def get_all_prices(self, city: str = "Delhi") -> List[GoldPrice]:
        prices = list(self._prices.values())
        for p in prices:
            p.city = city
        return prices
