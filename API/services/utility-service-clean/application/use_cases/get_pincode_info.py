"""Get Pincode Info Use Case."""
from domain.repositories import PincodeRepository
from application.dto import PincodeRequest, PincodeResponse
from application.dto.pincode_dto import PincodeInfoDTO


class PincodeNotFoundError(Exception):
    """Raised when pincode is not found."""
    pass


class GetPincodeInfoUseCase:
    """Use case for getting pincode information."""

    def __init__(self, pincode_repository: PincodeRepository):
        self.pincode_repository = pincode_repository

    async def execute(self, request: PincodeRequest) -> PincodeResponse:
        """Get pincode information."""
        infos = await self.pincode_repository.get_by_pincode(request.pincode)

        if not infos:
            raise PincodeNotFoundError(f"Pincode {request.pincode} not found")

        return PincodeResponse(
            success=True,
            data=[
                PincodeInfoDTO(
                    pincode=info.pincode,
                    post_office=info.post_office,
                    district=info.district,
                    state=info.state,
                    country=info.country,
                    delivery_status=info.delivery_status,
                    division=info.division,
                    region=info.region
                )
                for info in infos
            ]
        )
