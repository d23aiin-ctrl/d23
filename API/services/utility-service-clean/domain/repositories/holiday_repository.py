"""Holiday Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from domain.entities import Holiday, HolidayType


class HolidayRepository(ABC):
    """Abstract repository for holiday calendar."""

    @abstractmethod
    async def get_holidays(
        self,
        year: int,
        state: Optional[str] = None,
        holiday_type: Optional[HolidayType] = None
    ) -> List[Holiday]:
        """Get holidays for year with optional filters."""
        pass

    @abstractmethod
    async def get_upcoming_holidays(self, days: int = 30) -> List[Holiday]:
        """Get upcoming holidays within days."""
        pass
