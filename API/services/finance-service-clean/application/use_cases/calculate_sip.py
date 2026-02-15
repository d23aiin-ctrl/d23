"""Calculate SIP Use Case."""
from domain.entities import SIPCalculation
from domain.repositories import SIPRepository
from application.dto import SIPRequest, SIPResponse


class SIPValidationError(Exception):
    """Raised when SIP request validation fails."""
    pass


class CalculateSIPUseCase:
    """Use case for calculating SIP returns."""

    def __init__(self, sip_repository: SIPRepository):
        self.sip_repository = sip_repository

    async def execute(self, request: SIPRequest) -> SIPResponse:
        """Calculate SIP returns based on request parameters."""
        if request.monthly_investment <= 0:
            raise SIPValidationError("Monthly investment must be positive")

        if request.duration_years <= 0:
            raise SIPValidationError("Duration must be positive")

        calculation = SIPCalculation(
            monthly_investment=request.monthly_investment,
            duration_years=request.duration_years,
            expected_return_rate=request.expected_return_rate
        )
        calculation.calculate()

        return SIPResponse(
            success=True,
            monthly_investment=calculation.monthly_investment,
            duration_years=calculation.duration_years,
            expected_return_rate=calculation.expected_return_rate,
            total_invested=round(calculation.total_invested, 2),
            estimated_returns=round(calculation.estimated_returns, 2),
            maturity_value=round(calculation.maturity_value, 2)
        )
