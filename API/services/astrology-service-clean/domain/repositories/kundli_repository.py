"""
Kundli Repository Interface.

Abstract interface for birth chart calculations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities import Kundli, BirthDetails, Dosha


class KundliRepository(ABC):
    """
    Abstract repository for kundli operations.

    Implementations may use:
    - Swiss Ephemeris for calculations
    - External astrology API
    - Pre-computed data
    """

    @abstractmethod
    async def generate_kundli(
        self,
        birth_details: BirthDetails
    ) -> Optional[Kundli]:
        """
        Generate birth chart from birth details.

        Args:
            birth_details: Name, date/time, place, coordinates

        Returns:
            Complete Kundli with planets, houses, doshas
        """
        pass

    @abstractmethod
    async def get_doshas(
        self,
        kundli: Kundli
    ) -> List[Dosha]:
        """
        Analyze doshas in a kundli.

        Args:
            kundli: The birth chart

        Returns:
            List of doshas with severity and remedies
        """
        pass

    @abstractmethod
    async def match_kundlis(
        self,
        kundli1: Kundli,
        kundli2: Kundli
    ) -> dict:
        """
        Match two kundlis for compatibility (marriage matching).

        Args:
            kundli1: First person's kundli
            kundli2: Second person's kundli

        Returns:
            Matching score and details (Guna Milan)
        """
        pass
