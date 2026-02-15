"""IFSC API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import IFSCRequest, IFSCResponse
from application.use_cases import GetIFSCInfoUseCase
from application.use_cases.get_ifsc_info import IFSCNotFoundError
from infrastructure.api.dependencies import get_ifsc_info_use_case

router = APIRouter(prefix="/ifsc", tags=["IFSC"])


@router.get("/{ifsc}", response_model=IFSCResponse)
async def get_ifsc_info(
    ifsc: str,
    use_case: GetIFSCInfoUseCase = Depends(get_ifsc_info_use_case)
) -> IFSCResponse:
    """Get IFSC code information."""
    try:
        request = IFSCRequest(ifsc=ifsc)
        return await use_case.execute(request)
    except IFSCNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
