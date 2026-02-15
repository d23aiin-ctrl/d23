"""Client for Astrology Service (port 8003)."""

from clients.base_client import BaseServiceClient


class AstrologyClient(BaseServiceClient):
    """Async client for the Astrology microservice."""

    def __init__(self, base_url: str = "http://localhost:8003", **kwargs):
        super().__init__(base_url, service_name="Astrology Service", **kwargs)

    async def get_horoscope(self, sign: str, period: str = "daily") -> dict:
        return await self.get(f"/horoscope/{sign}", params={"period": period})

    async def generate_kundli(
        self,
        name: str,
        date: str,
        time: str,
        place: str,
        latitude: float,
        longitude: float,
        timezone: str = "Asia/Kolkata",
    ) -> dict:
        return await self.post("/kundli", json={
            "name": name,
            "date": date,
            "time": time,
            "place": place,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
        })

    async def match_kundli(self, person1: dict, person2: dict) -> dict:
        return await self.post("/kundli/match", json={
            "person1": person1,
            "person2": person2,
        })

    async def get_panchang(self, date: str | None = None, city: str = "Delhi") -> dict:
        params = {"city": city}
        if date:
            params["date"] = date
        return await self.get("/panchang", params=params)
