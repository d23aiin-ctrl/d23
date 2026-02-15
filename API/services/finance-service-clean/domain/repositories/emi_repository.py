"""EMI Repository Interface."""
from abc import ABC, abstractmethod
from typing import List
from domain.entities import EMICalculation, LoanType


class EMIRepository(ABC):
    """Abstract repository for EMI calculations."""

    @abstractmethod
    async def save_calculation(self, calculation: EMICalculation) -> str:
        """Save EMI calculation and return ID."""
        pass

    @abstractmethod
    async def get_calculation(self, calculation_id: str) -> EMICalculation:
        """Retrieve saved calculation by ID."""
        pass

    @abstractmethod
    async def get_interest_rates(self, loan_type: LoanType) -> List[float]:
        """Get typical interest rates for loan type."""
        pass
