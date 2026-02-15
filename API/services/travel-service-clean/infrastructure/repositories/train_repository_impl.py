"""
Train Repository Implementation.

Production implementation for train data.
"""

from typing import Optional, List
from datetime import date, time, timedelta, datetime
import httpx
import logging

from domain.repositories import TrainRepository
from domain.entities import Train, TrainSchedule, Station, StationStop, TrainType

logger = logging.getLogger(__name__)


class TrainRepositoryImpl(TrainRepository):
    """
    Production train repository.

    Calls external Railway API.
    """

    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    async def get_by_number(self, train_number: str) -> Optional[Train]:
        """Get train from API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/train/{train_number}",
                    headers={"X-API-Key": self.api_key}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return self._to_train_entity(response.json())

        except httpx.HTTPError as e:
            logger.error(f"API error: {e}")
            raise

    async def get_schedule(self, train_number: str) -> Optional[TrainSchedule]:
        """Get train schedule from API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/train/{train_number}/schedule",
                    headers={"X-API-Key": self.api_key}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return self._to_schedule_entity(response.json())

        except httpx.HTTPError as e:
            logger.error(f"API error: {e}")
            raise

    async def search(
        self,
        from_station: str,
        to_station: str,
        journey_date: Optional[date] = None
    ) -> List[Train]:
        """Search trains between stations."""
        try:
            params = {"from": from_station, "to": to_station}
            if journey_date:
                params["date"] = journey_date.strftime("%d-%m-%Y")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/trains/search",
                    params=params,
                    headers={"X-API-Key": self.api_key}
                )

                response.raise_for_status()
                data = response.json()

                return [
                    self._to_train_entity(t)
                    for t in data.get("trains", [])
                ]

        except httpx.HTTPError as e:
            logger.error(f"API error: {e}")
            return []

    async def get_live_status(
        self,
        train_number: str,
        journey_date: date
    ) -> Optional[dict]:
        """Get live status from API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/train/{train_number}/status",
                    params={"date": journey_date.strftime("%d-%m-%Y")},
                    headers={"X-API-Key": self.api_key}
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"API error: {e}")
            return None

    def _to_train_entity(self, data: dict) -> Train:
        """Transform API response to Train entity."""
        train_type_map = {
            "rajdhani": TrainType.RAJDHANI,
            "shatabdi": TrainType.SHATABDI,
            "duronto": TrainType.DURONTO,
            "superfast": TrainType.SUPERFAST,
            "express": TrainType.EXPRESS,
        }

        return Train(
            number=data["train_number"],
            name=data["train_name"],
            train_type=train_type_map.get(
                data.get("type", "").lower(),
                TrainType.EXPRESS
            ),
            source=Station(data["source"], data["source_name"]),
            destination=Station(data["destination"], data["destination_name"]),
            departure_time=datetime.strptime(data["departure"], "%H:%M").time(),
            arrival_time=datetime.strptime(data["arrival"], "%H:%M").time(),
            duration=self._parse_duration(data.get("duration", "0h 0m")),
            distance_km=data.get("distance_km", 0),
            runs_on=data.get("runs_on", []),
            classes=data.get("classes", []),
            has_pantry=data.get("has_pantry", False),
        )

    def _to_schedule_entity(self, data: dict) -> TrainSchedule:
        """Transform API response to TrainSchedule entity."""
        train = self._to_train_entity(data)

        stops = []
        for s in data.get("stops", []):
            stops.append(StationStop(
                station=Station(s["station_code"], s["station_name"]),
                arrival=datetime.strptime(s["arrival"], "%H:%M").time() if s.get("arrival") else None,
                departure=datetime.strptime(s["departure"], "%H:%M").time() if s.get("departure") else None,
                day=s.get("day", 1),
                distance_km=s.get("distance_km", 0),
                halt_minutes=s.get("halt_minutes"),
                platform=s.get("platform"),
            ))

        return TrainSchedule(train=train, stops=stops)

    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '17h 30m' to timedelta."""
        hours = 0
        minutes = 0

        if "h" in duration_str:
            parts = duration_str.split("h")
            hours = int(parts[0].strip())
            if len(parts) > 1 and "m" in parts[1]:
                minutes = int(parts[1].replace("m", "").strip())

        return timedelta(hours=hours, minutes=minutes)
