"""
PNR Repository Implementation.

Production implementation that calls external Railway API.
"""

from typing import Optional
from datetime import datetime
import httpx
import logging

from domain.repositories import PNRRepository
from domain.entities import PNR, Passenger, BookingStatus

logger = logging.getLogger(__name__)


class PNRRepositoryImpl(PNRRepository):
    """
    Production PNR repository.

    Calls external Railway API and transforms response to domain entities.
    """

    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    async def get_by_pnr(self, pnr_number: str) -> Optional[PNR]:
        """
        Get PNR status from Railway API.

        In production, this would call the actual Railway API.
        """
        logger.info(f"Fetching PNR {pnr_number} from API")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/pnr/{pnr_number}",
                    headers={"X-API-Key": self.api_key}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                data = response.json()

                return self._to_entity(data)

        except httpx.HTTPError as e:
            logger.error(f"API error fetching PNR: {e}")
            raise

    async def get_fare(
        self,
        train_number: str,
        from_station: str,
        to_station: str,
        travel_class: str
    ) -> Optional[float]:
        """Get fare from API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/fare",
                    params={
                        "train": train_number,
                        "from": from_station,
                        "to": to_station,
                        "class": travel_class
                    },
                    headers={"X-API-Key": self.api_key}
                )

                if response.status_code == 200:
                    return response.json().get("fare")

                return None

        except httpx.HTTPError as e:
            logger.error(f"API error fetching fare: {e}")
            return None

    def _to_entity(self, data: dict) -> PNR:
        """Transform API response to domain entity."""
        passengers = [
            Passenger(
                number=p["number"],
                booking_status=BookingStatus.from_string(p["booking_status"]),
                current_status=BookingStatus.from_string(p["current_status"]),
                coach=p.get("coach"),
                berth=p.get("berth"),
                berth_type=p.get("berth_type"),
            )
            for p in data.get("passengers", [])
        ]

        return PNR(
            pnr_number=data["pnr"],
            train_number=data["train_number"],
            train_name=data["train_name"],
            journey_date=datetime.strptime(data["doj"], "%d-%m-%Y").date(),
            from_station_code=data["from_station"],
            from_station_name=data["from_station_name"],
            to_station_code=data["to_station"],
            to_station_name=data["to_station_name"],
            travel_class=data["class"],
            passengers=passengers,
            chart_prepared=data.get("chart_prepared", False),
            booking_fare=data.get("fare"),
        )
