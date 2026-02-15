"""Driving License Router."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from application.dto import DLRequest, DLResponse
from application.use_cases import GetDLStatusUseCase
from application.use_cases.get_dl_status import DLValidationError, DLNotFoundError
from infrastructure.api.dependencies import get_dl_use_case

router = APIRouter(prefix="/dl", tags=["Driving License"])

@router.post("", response_model=DLResponse)
async def get_dl_status(
    request: DLRequest,
    use_case: Annotated[GetDLStatusUseCase, Depends(get_dl_use_case)]
):
    try:
        return await use_case.execute(request)
    except DLValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DLNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
