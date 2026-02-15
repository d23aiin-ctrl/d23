"""
Panchang Repository Interface.

Abstract interface for Hindu calendar data.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from domain.entities import Panchang


class PanchangRepository(ABC):
    """
    Abstract repository for panchang operations.

    Implementations may use:
    - Astronomical calculations
    - Pre-computed calendar data
    - External panchang API
    """

    @abstractmethod
    async def get_panchang(
        self,
        target_date: date,
        city: str,
        latitude: float,
        longitude: float
    ) -> Optional[Panchang]:
        """
        Get panchang for a specific date and location.

        Args:
            target_date: Date for panchang
            city: City name
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Complete Panchang with all five limbs
        """
        pass

    @abstractmethod
    async def get_festivals(
        self,
        month: int,
        year: int
    ) -> List[dict]:
        """
        Get festivals for a month.

        Args:
            month: Month number (1-12)
            year: Year

        Returns:
            List of festivals with dates
        """
        pass

    @abstractmethod
    async def get_auspicious_dates(
        self,
        purpose: str,
        start_date: date,
        end_date: date
    ) -> List[date]:
        """
        Get auspicious dates for a purpose.

        Args:
            purpose: "marriage", "travel", "business", etc.
            start_date: Range start
            end_date: Range end

        Returns:
            List of auspicious dates
        """
        pass
