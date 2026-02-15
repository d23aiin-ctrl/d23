"""Mock EMI Repository Implementation."""
from typing import List, Dict
import uuid
from domain.entities import EMICalculation, LoanType
from domain.repositories import EMIRepository


class MockEMIRepository(EMIRepository):
    """Mock implementation of EMI repository for testing."""

    def __init__(self):
        self._calculations: Dict[str, EMICalculation] = {}
        self._interest_rates = {
            LoanType.HOME: [7.0, 7.5, 8.0, 8.5, 9.0],
            LoanType.CAR: [8.5, 9.0, 9.5, 10.0, 10.5],
            LoanType.PERSONAL: [10.5, 11.0, 12.0, 14.0, 16.0],
            LoanType.EDUCATION: [8.0, 8.5, 9.0, 9.5, 10.0],
        }

    async def save_calculation(self, calculation: EMICalculation) -> str:
        calc_id = str(uuid.uuid4())
        self._calculations[calc_id] = calculation
        return calc_id

    async def get_calculation(self, calculation_id: str) -> EMICalculation:
        return self._calculations.get(calculation_id)

    async def get_interest_rates(self, loan_type: LoanType) -> List[float]:
        return self._interest_rates.get(loan_type, [10.0])
