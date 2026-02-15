"""
Horoscope Repository Interface.

Abstract interface for horoscope data access.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from domain.entities import Horoscope, ZodiacSign, HoroscopePeriod


class HoroscopeRepository(ABC):
    """
    Abstract repository for horoscope operations.

    Implementations may fetch from:
    - External API
    - Database cache
    - Generated predictions
    """

    @abstractmethod
    async def get_horoscope(
        self,
        sign: ZodiacSign,
        period: HoroscopePeriod,
        target_date: Optional[date] = None
    ) -> Optional[Horoscope]:
        """
        Get horoscope for a zodiac sign.

        Args:
            sign: Zodiac sign
            period: daily/weekly/monthly
            target_date: Date for prediction (default: today)

        Returns:
            Horoscope entity or None if not available
        """
        pass

    @abstractmethod
    async def get_compatibility(
        self,
        sign1: ZodiacSign,
        sign2: ZodiacSign
    ) -> dict:
        """
        Get compatibility between two signs.

        Args:
            sign1: First zodiac sign
            sign2: Second zodiac sign

        Returns:
            Compatibility data
        """
        pass
