"""PM-KISAN Router."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from application.dto import PMKisanRequest, PMKisanResponse
from application.use_cases import GetPMKisanStatusUseCase
from application.use_cases.get_pmkisan_status import PMKisanValidationError, PMKisanNotFoundError
from infrastructure.api.dependencies import get_pmkisan_use_case

router = APIRouter(prefix="/pmkisan", tags=["PM-KISAN"])

@router.post("", response_model=PMKisanResponse)
async def get_pmkisan_status(
    request: PMKisanRequest,
    use_case: Annotated[GetPMKisanStatusUseCase, Depends(get_pmkisan_use_case)]
):
    try:
        return await use_case.execute(request)
    except PMKisanValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PMKisanNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
