"""EMI API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import EMIRequest, EMIResponse
from application.use_cases import CalculateEMIUseCase
from application.use_cases.calculate_emi import EMIValidationError
from infrastructure.api.dependencies import get_calculate_emi_use_case

router = APIRouter(prefix="/emi", tags=["EMI Calculator"])


@router.post("/calculate", response_model=EMIResponse)
async def calculate_emi(
    request: EMIRequest,
    use_case: CalculateEMIUseCase = Depends(get_calculate_emi_use_case)
) -> EMIResponse:
    """Calculate EMI for loan."""
    try:
        return await use_case.execute(request)
    except EMIValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
