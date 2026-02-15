"""PM-KISAN Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import PMKisanBeneficiary


class PMKisanRepository(ABC):
    """Abstract repository for PM-KISAN operations."""

    @abstractmethod
    async def get_by_mobile(self, mobile: str) -> Optional[PMKisanBeneficiary]:
        """Get beneficiary by mobile number."""
        pass

    @abstractmethod
    async def get_by_aadhaar(self, aadhaar: str) -> Optional[PMKisanBeneficiary]:
        """Get beneficiary by Aadhaar number."""
        pass

    @abstractmethod
    async def get_by_registration(self, registration_number: str) -> Optional[PMKisanBeneficiary]:
        """Get beneficiary by registration number."""
        pass
