"""
Mock Train Repository.

Used for testing and development.
"""

from typing import Optional, List
from datetime import date, time, timedelta

from domain.repositories import TrainRepository
from domain.entities import Train, TrainSchedule, Station, StationStop, TrainType


class MockTrainRepository(TrainRepository):
    """
    Mock repository for testing.
    """

    def __init__(self):
        # Predefined stations
        self._stations = {
            "NDLS": Station("NDLS", "New Delhi", "NR", "Delhi"),
            "HWH": Station("HWH", "Howrah Junction", "ER", "West Bengal"),
            "BCT": Station("BCT", "Mumbai Central", "WR", "Maharashtra"),
            "CNB": Station("CNB", "Kanpur Central", "NCR", "Uttar Pradesh"),
            "ALD": Station("ALD", "Prayagraj Junction", "NCR", "Uttar Pradesh"),
            "MGS": Station("MGS", "Mughal Sarai Junction", "ECR", "Uttar Pradesh"),
        }

        # Predefined trains
        self._trains = {
            "12301": Train(
                number="12301",
                name="Howrah Rajdhani Express",
                train_type=TrainType.RAJDHANI,
                source=self._stations["NDLS"],
                destination=self._stations["HWH"],
                departure_time=time(16, 55),
                arrival_time=time(9, 55),
                duration=timedelta(hours=17),
                distance_km=1447,
                runs_on=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                classes=["1A", "2A", "3A"],
                has_pantry=True
            ),
            "12951": Train(
                number="12951",
                name="Mumbai Rajdhani Express",
                train_type=TrainType.RAJDHANI,
                source=self._stations["NDLS"],
                destination=self._stations["BCT"],
                departure_time=time(16, 35),
                arrival_time=time(8, 35),
                duration=timedelta(hours=16),
                distance_km=1384,
                runs_on=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                classes=["1A", "2A", "3A"],
                has_pantry=True
            ),
        }

    async def get_by_number(self, train_number: str) -> Optional[Train]:
        """Get train by number."""
        return self._trains.get(train_number)

    async def get_schedule(self, train_number: str) -> Optional[TrainSchedule]:
        """Get train schedule."""
        train = self._trains.get(train_number)
        if not train:
            return None

        # Create mock schedule for Rajdhani
        if train_number == "12301":
            stops = [
                StationStop(self._stations["NDLS"], None, time(16, 55), 1, 0, None, "16"),
                StationStop(self._stations["CNB"], time(21, 25), time(21, 35), 1, 440, 10, "1"),
                StationStop(self._stations["ALD"], time(23, 35), time(23, 45), 1, 634, 10, "6"),
                StationStop(self._stations["MGS"], time(1, 15), time(1, 25), 2, 780, 10, "1"),
                StationStop(self._stations["HWH"], time(9, 55), None, 2, 1447, None, "9"),
            ]
            return TrainSchedule(train=train, stops=stops)

        return TrainSchedule(train=train, stops=[])

    async def search(
        self,
        from_station: str,
        to_station: str,
        journey_date: Optional[date] = None
    ) -> List[Train]:
        """Search trains between stations."""
        results = []

        for train in self._trains.values():
            # Simple check - in reality would check route
            if (train.source.code == from_station and
                train.destination.code == to_station):
                results.append(train)

        return results

    async def get_live_status(
        self,
        train_number: str,
        journey_date: date
    ) -> Optional[dict]:
        """Get mock live status."""
        train = self._trains.get(train_number)
        if not train:
            return None

        return {
            "train_number": train_number,
            "train_name": train.name,
            "current_station": "CNB",
            "current_station_name": "Kanpur Central",
            "delay_minutes": 15,
            "last_updated": "2026-02-04 21:40",
            "stations": [
                {"code": "NDLS", "name": "New Delhi", "delay": 15, "departed": True},
                {"code": "CNB", "name": "Kanpur Central", "delay": 15, "arrived": True},
            ]
        }
