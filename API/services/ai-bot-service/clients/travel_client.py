"""Client for Travel Service (port 8004)."""

from clients.base_client import BaseServiceClient


class TravelClient(BaseServiceClient):
    """Async client for the Travel microservice."""

    def __init__(self, base_url: str = "http://localhost:8004", **kwargs):
        super().__init__(base_url, service_name="Travel Service", **kwargs)

    async def get_pnr_status(self, pnr_number: str) -> dict:
        return await self.get(f"/pnr/{pnr_number}")

    async def get_train_schedule(self, train_number: str) -> dict:
        return await self.get(f"/train/{train_number}/schedule")

    async def get_train_status(self, train_number: str, date: str | None = None) -> dict:
        params = {}
        if date:
            params["date"] = date
        return await self.get(f"/train/{train_number}/status", params=params or None)

    async def search_trains(self, from_station: str, to_station: str, date: str | None = None) -> dict:
        params = {"from": from_station, "to": to_station}
        if date:
            params["date"] = date
        return await self.get("/trains/search", params=params)
