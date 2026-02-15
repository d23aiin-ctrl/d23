"""Pincode API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import PincodeRequest, PincodeResponse
from application.use_cases import GetPincodeInfoUseCase
from application.use_cases.get_pincode_info import PincodeNotFoundError
from infrastructure.api.dependencies import get_pincode_info_use_case

router = APIRouter(prefix="/pincode", tags=["Pincode"])


@router.get("/{pincode}", response_model=PincodeResponse)
async def get_pincode_info(
    pincode: str,
    use_case: GetPincodeInfoUseCase = Depends(get_pincode_info_use_case)
) -> PincodeResponse:
    """Get pincode information."""
    try:
        request = PincodeRequest(pincode=pincode)
        return await use_case.execute(request)
    except PincodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
