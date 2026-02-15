"""Get Driving License Status Use Case."""
from dataclasses import dataclass
from domain.repositories import DLRepository
from application.dto import DLRequest, DLResponse, VehicleClassDTO

class DLValidationError(Exception):
    pass

class DLNotFoundError(Exception):
    pass

@dataclass
class GetDLStatusUseCase:
    dl_repository: DLRepository

    async def execute(self, request: DLRequest) -> DLResponse:
        if not request.dl_number or len(request.dl_number) < 10:
            raise DLValidationError("Valid DL number required (min 10 characters)")

        if request.dob:
            dl = await self.dl_repository.verify_dl(request.dl_number, request.dob)
        else:
            dl = await self.dl_repository.get_by_dl_number(request.dl_number)

        if not dl:
            raise DLNotFoundError(f"DL {request.dl_number} not found")

        vehicle_classes = [
            VehicleClassDTO(code=vc.code, description=vc.description)
            for vc in dl.vehicle_classes
        ]

        return DLResponse(
            dl_number=dl.dl_number,
            name=dl.name,
            father_name=dl.father_name,
            date_of_birth=dl.date_of_birth.strftime("%Y-%m-%d"),
            blood_group=dl.blood_group,
            address=dl.address,
            state=dl.state,
            rto_code=dl.rto_code,
            issue_date=dl.issue_date.strftime("%Y-%m-%d"),
            validity_nt=dl.validity_nt.strftime("%Y-%m-%d"),
            validity_trans=dl.validity_trans.strftime("%Y-%m-%d") if dl.validity_trans else None,
            status=dl.status.value,
            is_valid=dl.is_valid,
            days_to_expiry=dl.days_to_expiry,
            vehicle_classes=vehicle_classes
        )
