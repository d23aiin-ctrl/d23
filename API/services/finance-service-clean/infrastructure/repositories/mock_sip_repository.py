"""Mock SIP Repository Implementation."""
from typing import List, Dict
import uuid
from domain.entities import SIPCalculation
from domain.repositories import SIPRepository


class MockSIPRepository(SIPRepository):
    """Mock implementation of SIP repository for testing."""

    def __init__(self):
        self._calculations: Dict[str, SIPCalculation] = {}
        self._historical_returns = {
            "equity": [12.0, 15.0, 10.0, 18.0, 14.0],
            "debt": [7.0, 8.0, 6.5, 7.5, 8.5],
            "hybrid": [10.0, 11.0, 9.0, 12.0, 10.5],
            "elss": [14.0, 16.0, 12.0, 20.0, 15.0],
        }

    async def save_calculation(self, calculation: SIPCalculation) -> str:
        calc_id = str(uuid.uuid4())
        self._calculations[calc_id] = calculation
        return calc_id

    async def get_calculation(self, calculation_id: str) -> SIPCalculation:
        return self._calculations.get(calculation_id)

    async def get_historical_returns(self, fund_type: str, years: int) -> List[float]:
        returns = self._historical_returns.get(fund_type.lower(), [10.0])
        return returns[:years] if years < len(returns) else returns
