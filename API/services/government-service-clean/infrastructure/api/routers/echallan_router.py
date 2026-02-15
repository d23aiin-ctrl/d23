"""E-Challan Router."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from application.dto import EChallanRequest, EChallanListResponse
from application.use_cases import GetEChallansUseCase
from application.use_cases.get_echallans import EChallanValidationError, EChallanNotFoundError
from infrastructure.api.dependencies import get_echallan_use_case

router = APIRouter(prefix="/echallan", tags=["E-Challan"])

@router.post("", response_model=EChallanListResponse)
async def get_echallans(
    request: EChallanRequest,
    use_case: Annotated[GetEChallansUseCase, Depends(get_echallan_use_case)]
):
    try:
        return await use_case.execute(request)
    except EChallanValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EChallanNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
