"""
PNR Repository Interface.

Abstract interface for PNR data access.
This is a PORT in hexagonal architecture terms.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..entities import PNR


class PNRRepository(ABC):
    """
    Abstract repository for PNR operations.

    Implementations can be:
    - RailwayAPIRepository (calls external Railway API)
    - ScrapingRepository (scrapes IRCTC website)
    - CachedRepository (decorator with Redis cache)
    - MockRepository (for testing)
    """

    @abstractmethod
    async def get_by_pnr(self, pnr_number: str) -> Optional[PNR]:
        """
        Get PNR status by PNR number.

        Args:
            pnr_number: 10-digit PNR number

        Returns:
            PNR entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_fare(
        self,
        train_number: str,
        from_station: str,
        to_station: str,
        travel_class: str
    ) -> Optional[float]:
        """
        Get fare for a journey.

        Args:
            train_number: Train number
            from_station: Source station code
            to_station: Destination station code
            travel_class: Travel class (SL, 3A, 2A, 1A)

        Returns:
            Fare amount or None if not available
        """
        pass
