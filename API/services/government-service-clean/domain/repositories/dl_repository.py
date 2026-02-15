"""Driving License Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import DrivingLicense


class DLRepository(ABC):
    """Abstract repository for driving license operations."""

    @abstractmethod
    async def get_by_dl_number(self, dl_number: str) -> Optional[DrivingLicense]:
        """Get DL by number."""
        pass

    @abstractmethod
    async def verify_dl(self, dl_number: str, dob: str) -> Optional[DrivingLicense]:
        """Verify DL with date of birth."""
        pass
