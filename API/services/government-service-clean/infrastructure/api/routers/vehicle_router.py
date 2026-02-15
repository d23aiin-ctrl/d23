"""Vehicle Router."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from application.dto import VehicleResponse
from application.use_cases import GetVehicleRCUseCase
from application.use_cases.get_vehicle_rc import VehicleValidationError, VehicleNotFoundError
from infrastructure.api.dependencies import get_vehicle_use_case

router = APIRouter(prefix="/vehicle", tags=["Vehicle RC"])

@router.get("/{vehicle_number}", response_model=VehicleResponse)
async def get_vehicle_rc(
    vehicle_number: str,
    use_case: Annotated[GetVehicleRCUseCase, Depends(get_vehicle_use_case)]
):
    try:
        return await use_case.execute(vehicle_number)
    except VehicleValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VehicleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
