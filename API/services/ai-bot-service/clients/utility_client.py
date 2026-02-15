"""Client for Utility Service (port 8006)."""

from clients.base_client import BaseServiceClient


class UtilityClient(BaseServiceClient):
    """Async client for the Utility microservice."""

    def __init__(self, base_url: str = "http://localhost:8006", **kwargs):
        super().__init__(base_url, service_name="Utility Service", **kwargs)

    async def get_weather(self, city: str) -> dict:
        return await self.get(f"/weather/{city}")

    async def get_gold_price(self, city: str = "Delhi") -> dict:
        return await self.get("/gold/", params={"city": city})

    async def get_fuel_price(self, city: str) -> dict:
        return await self.get(f"/fuel/{city}")

    async def get_currency_rate(self, base: str = "USD", quote: str = "INR") -> dict:
        return await self.get("/currency/rate", params={"base": base, "quote": quote})

    async def convert_currency(self, amount: float, base: str, quote: str) -> dict:
        return await self.post("/currency/convert", json={
            "amount": amount,
            "base": base,
            "quote": quote,
        })

    async def get_pincode_info(self, pincode: str) -> dict:
        return await self.get(f"/pincode/{pincode}")

    async def get_ifsc_info(self, ifsc: str) -> dict:
        return await self.get(f"/ifsc/{ifsc}")

    async def get_holidays(self, year: int = 2024, state: str | None = None) -> dict:
        params: dict = {"year": year}
        if state:
            params["state"] = state
        return await self.get("/holidays/", params=params)
