"""
Train Repository Interface.

Abstract interface for train data access.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from ..entities import Train, TrainSchedule


class TrainRepository(ABC):
    """
    Abstract repository for train operations.

    Implementations can be:
    - RailwayAPIRepository (calls external Railway API)
    - DatabaseRepository (local database cache)
    - MockRepository (for testing)
    """

    @abstractmethod
    async def get_by_number(self, train_number: str) -> Optional[Train]:
        """
        Get train by number.

        Args:
            train_number: 5-digit train number

        Returns:
            Train entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_schedule(self, train_number: str) -> Optional[TrainSchedule]:
        """
        Get complete train schedule with all stops.

        Args:
            train_number: 5-digit train number

        Returns:
            TrainSchedule with all stops
        """
        pass

    @abstractmethod
    async def search(
        self,
        from_station: str,
        to_station: str,
        date: Optional[date] = None
    ) -> List[Train]:
        """
        Search trains between stations.

        Args:
            from_station: Source station code
            to_station: Destination station code
            date: Optional journey date to filter by running days

        Returns:
            List of trains between the stations
        """
        pass

    @abstractmethod
    async def get_live_status(
        self,
        train_number: str,
        journey_date: date
    ) -> Optional[dict]:
        """
        Get live running status of a train.

        Args:
            train_number: Train number
            journey_date: Date of journey

        Returns:
            Live status data
        """
        pass
