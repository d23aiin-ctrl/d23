"""Get IFSC Info Use Case."""
from domain.repositories import IFSCRepository
from application.dto import IFSCRequest, IFSCResponse
from application.dto.ifsc_dto import IFSCInfoDTO


class IFSCNotFoundError(Exception):
    """Raised when IFSC code is not found."""
    pass


class GetIFSCInfoUseCase:
    """Use case for getting IFSC information."""

    def __init__(self, ifsc_repository: IFSCRepository):
        self.ifsc_repository = ifsc_repository

    async def execute(self, request: IFSCRequest) -> IFSCResponse:
        """Get IFSC information."""
        info = await self.ifsc_repository.get_by_ifsc(request.ifsc)

        if not info:
            raise IFSCNotFoundError(f"IFSC code {request.ifsc} not found")

        return IFSCResponse(
            success=True,
            data=IFSCInfoDTO(
                ifsc=info.ifsc,
                bank_name=info.bank_name,
                branch=info.branch,
                address=info.address,
                city=info.city,
                district=info.district,
                state=info.state,
                contact=info.contact,
                upi=info.upi,
                rtgs=info.rtgs,
                neft=info.neft,
                imps=info.imps,
                micr=info.micr
            )
        )
