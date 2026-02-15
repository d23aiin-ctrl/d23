"""
Kundli API Router.

Birth chart and matching endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from application.dto import (
    KundliRequest, KundliResponse,
    MatchingRequest, MatchingResponse
)
from application.use_cases import GenerateKundliUseCase, MatchKundliUseCase
from application.use_cases.generate_kundli import (
    KundliValidationError,
    KundliGenerationError
)
from application.use_cases.match_kundli import MatchingError
from infrastructure.api.dependencies import (
    get_kundli_use_case,
    get_matching_use_case
)

router = APIRouter(prefix="/kundli", tags=["Kundli"])


@router.post(
    "",
    response_model=KundliResponse,
    summary="Generate Kundli",
    description="Generate birth chart from birth details"
)
async def generate_kundli(
    request: KundliRequest,
    use_case: Annotated[GenerateKundliUseCase, Depends(get_kundli_use_case)]
):
    """
    Generate birth chart (Janam Kundli).

    - **name**: Person's name
    - **date**: Birth date (YYYY-MM-DD)
    - **time**: Birth time (HH:MM)
    - **place**: Birth place
    - **latitude/longitude**: Coordinates
    """
    try:
        return await use_case.execute(request)
    except KundliValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KundliGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/match",
    response_model=MatchingResponse,
    summary="Match Kundlis",
    description="Match two kundlis for marriage compatibility"
)
async def match_kundlis(
    request: MatchingRequest,
    use_case: Annotated[MatchKundliUseCase, Depends(get_matching_use_case)]
):
    """
    Kundli matching (Guna Milan) for marriage compatibility.

    Calculates Ashtakoot matching (36 points system):
    - Varna, Vashya, Tara, Yoni
    - Graha Maitri, Gana, Bhakoot, Nadi
    """
    try:
        return await use_case.execute(request)
    except KundliValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MatchingError as e:
        raise HTTPException(status_code=500, detail=str(e))
