"""Client for Government Service (port 8005)."""

from clients.base_client import BaseServiceClient


class GovernmentClient(BaseServiceClient):
    """Async client for the Government microservice."""

    def __init__(self, base_url: str = "http://localhost:8005", **kwargs):
        super().__init__(base_url, service_name="Government Service", **kwargs)

    async def check_pmkisan(
        self,
        mobile: str | None = None,
        aadhaar: str | None = None,
        registration_number: str | None = None,
    ) -> dict:
        body: dict = {}
        if mobile:
            body["mobile"] = mobile
        if aadhaar:
            body["aadhaar"] = aadhaar
        if registration_number:
            body["registration_number"] = registration_number
        return await self.post("/pmkisan", json=body)

    async def check_driving_license(self, dl_number: str, dob: str | None = None) -> dict:
        body: dict = {"dl_number": dl_number}
        if dob:
            body["dob"] = dob
        return await self.post("/dl", json=body)

    async def get_vehicle_info(self, vehicle_number: str) -> dict:
        return await self.get(f"/vehicle/{vehicle_number}")

    async def check_echallan(
        self,
        vehicle_number: str | None = None,
        challan_number: str | None = None,
    ) -> dict:
        body: dict = {}
        if vehicle_number:
            body["vehicle_number"] = vehicle_number
        if challan_number:
            body["challan_number"] = challan_number
        return await self.post("/echallan", json=body)
