"""
Train API Router.

HTTP layer for train-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, Optional

from application.dto import TrainScheduleResponse, TrainSearchResponse, LiveStatusDTO
from application.use_cases import (
    GetTrainScheduleUseCase,
    SearchTrainsUseCase,
    GetLiveStatusUseCase
)
from application.use_cases.get_train_schedule import (
    TrainValidationError,
    TrainNotFoundError
)
from application.use_cases.search_trains import StationValidationError
from application.use_cases.get_live_status import LiveStatusError
from infrastructure.api.dependencies import (
    get_schedule_use_case,
    get_search_use_case,
    get_live_status_use_case
)

router = APIRouter(tags=["Trains"])


@router.get(
    "/train/{train_number}/schedule",
    response_model=TrainScheduleResponse,
    summary="Get Train Schedule",
    description="Get complete schedule with all stops"
)
async def get_train_schedule(
    train_number: str,
    use_case: Annotated[GetTrainScheduleUseCase, Depends(get_schedule_use_case)]
):
    """
    Get train schedule with all stops.

    - **train_number**: 5-digit train number
    """
    try:
        return await use_case.execute(train_number)

    except TrainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except TrainNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/train/{train_number}/status",
    response_model=LiveStatusDTO,
    summary="Get Live Status",
    description="Get live running status of a train"
)
async def get_live_status(
    train_number: str,
    date: Optional[str] = Query(None, description="Journey date (DD-MM-YYYY)"),
    use_case: Annotated[GetLiveStatusUseCase, Depends(get_live_status_use_case)] = None
):
    """
    Get live train running status.

    - **train_number**: 5-digit train number
    - **date**: Optional journey date
    """
    try:
        return await use_case.execute(train_number, date)

    except LiveStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/trains/search",
    response_model=TrainSearchResponse,
    summary="Search Trains",
    description="Search trains between two stations"
)
async def search_trains(
    from_station: str = Query(..., alias="from", description="Source station code"),
    to_station: str = Query(..., alias="to", description="Destination station code"),
    date: Optional[str] = Query(None, description="Journey date (DD-MM-YYYY)"),
    use_case: Annotated[SearchTrainsUseCase, Depends(get_search_use_case)] = None
):
    """
    Search trains between stations.

    - **from**: Source station code (e.g., NDLS)
    - **to**: Destination station code (e.g., HWH)
    - **date**: Optional journey date
    """
    try:
        return await use_case.execute(from_station, to_station, date)

    except StationValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
