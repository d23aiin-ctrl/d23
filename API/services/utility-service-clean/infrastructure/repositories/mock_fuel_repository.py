"""Mock Fuel Repository Implementation."""
from typing import List, Optional
from datetime import datetime
from domain.entities import FuelPrice, FuelType
from domain.repositories import FuelRepository


class MockFuelRepository(FuelRepository):
    """Mock implementation of fuel repository for testing."""

    def __init__(self):
        self._city_data = {
            "delhi": {
                "state": "Delhi",
                "prices": {
                    FuelType.PETROL: 94.72,
                    FuelType.DIESEL: 87.62,
                    FuelType.CNG: 74.59,
                }
            },
            "mumbai": {
                "state": "Maharashtra",
                "prices": {
                    FuelType.PETROL: 103.44,
                    FuelType.DIESEL: 89.97,
                    FuelType.CNG: 79.50,
                }
            },
            "bangalore": {
                "state": "Karnataka",
                "prices": {
                    FuelType.PETROL: 101.94,
                    FuelType.DIESEL: 87.89,
                    FuelType.CNG: 72.00,
                }
            },
        }

    async def get_price(self, fuel_type: FuelType, city: str) -> Optional[FuelPrice]:
        city_data = self._city_data.get(city.lower())
        if not city_data:
            return None
        price = city_data["prices"].get(fuel_type)
        if not price:
            return None
        return FuelPrice(
            fuel_type=fuel_type,
            price=price,
            city=city.title(),
            state=city_data["state"],
            change=0.0,
            effective_date=datetime.now()
        )

    async def get_all_prices(self, city: str) -> List[FuelPrice]:
        city_data = self._city_data.get(city.lower())
        if not city_data:
            return []
        return [
            FuelPrice(
                fuel_type=fuel_type,
                price=price,
                city=city.title(),
                state=city_data["state"],
                change=0.0,
                effective_date=datetime.now()
            )
            for fuel_type, price in city_data["prices"].items()
        ]
