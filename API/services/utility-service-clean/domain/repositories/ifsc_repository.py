"""IFSC Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import IFSCInfo


class IFSCRepository(ABC):
    """Abstract repository for IFSC lookup."""

    @abstractmethod
    async def get_by_ifsc(self, ifsc: str) -> Optional[IFSCInfo]:
        """Get bank info by IFSC code."""
        pass
