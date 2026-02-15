"""Calculate EMI Use Case."""
from domain.entities import EMICalculation, LoanType
from domain.repositories import EMIRepository
from application.dto import EMIRequest, EMIResponse
from application.dto.emi_dto import LoanTypeDTO


class EMIValidationError(Exception):
    """Raised when EMI request validation fails."""
    pass


class CalculateEMIUseCase:
    """Use case for calculating EMI."""

    def __init__(self, emi_repository: EMIRepository):
        self.emi_repository = emi_repository

    def _map_loan_type(self, loan_type_dto: LoanTypeDTO) -> LoanType:
        mapping = {
            LoanTypeDTO.HOME: LoanType.HOME,
            LoanTypeDTO.CAR: LoanType.CAR,
            LoanTypeDTO.PERSONAL: LoanType.PERSONAL,
            LoanTypeDTO.EDUCATION: LoanType.EDUCATION,
        }
        return mapping[loan_type_dto]

    async def execute(self, request: EMIRequest) -> EMIResponse:
        """Calculate EMI based on request parameters."""
        if request.principal <= 0:
            raise EMIValidationError("Principal amount must be positive")

        if request.tenure_months <= 0:
            raise EMIValidationError("Tenure must be positive")

        loan_type = self._map_loan_type(request.loan_type)

        calculation = EMICalculation(
            principal=request.principal,
            annual_rate=request.annual_rate,
            tenure_months=request.tenure_months,
            loan_type=loan_type
        )
        calculation.calculate()

        return EMIResponse(
            success=True,
            principal=calculation.principal,
            annual_rate=calculation.annual_rate,
            tenure_months=calculation.tenure_months,
            loan_type=calculation.loan_type.value,
            monthly_emi=round(calculation.monthly_emi, 2),
            total_interest=round(calculation.total_interest, 2),
            total_amount=round(calculation.total_amount, 2)
        )
