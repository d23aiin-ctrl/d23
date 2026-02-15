"""SIP API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import SIPRequest, SIPResponse
from application.use_cases import CalculateSIPUseCase
from application.use_cases.calculate_sip import SIPValidationError
from infrastructure.api.dependencies import get_calculate_sip_use_case

router = APIRouter(prefix="/sip", tags=["SIP Calculator"])


@router.post("/calculate", response_model=SIPResponse)
async def calculate_sip(
    request: SIPRequest,
    use_case: CalculateSIPUseCase = Depends(get_calculate_sip_use_case)
) -> SIPResponse:
    """Calculate SIP returns."""
    try:
        return await use_case.execute(request)
    except SIPValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
