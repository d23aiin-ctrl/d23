"""
PNR API Router.

Thin HTTP layer that delegates to use cases.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from application.dto import PNRResponse
from application.use_cases import GetPNRStatusUseCase
from application.use_cases.get_pnr_status import (
    PNRValidationError,
    PNRNotFoundError
)
from infrastructure.api.dependencies import get_pnr_use_case

router = APIRouter(prefix="/pnr", tags=["PNR Status"])


@router.get(
    "/{pnr_number}",
    response_model=PNRResponse,
    summary="Get PNR Status",
    description="Get the current status of a PNR booking"
)
async def get_pnr_status(
    pnr_number: str,
    use_case: Annotated[GetPNRStatusUseCase, Depends(get_pnr_use_case)]
):
    """
    Get PNR status.

    - **pnr_number**: 10-digit PNR number

    Returns booking status with all passengers.
    """
    try:
        return await use_case.execute(pnr_number)

    except PNRValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except PNRNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
