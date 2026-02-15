"""Get PM-KISAN Status Use Case."""
from dataclasses import dataclass
from domain.repositories import PMKisanRepository
from application.dto import PMKisanRequest, PMKisanResponse, InstallmentDTO

class PMKisanValidationError(Exception):
    pass

class PMKisanNotFoundError(Exception):
    pass

@dataclass
class GetPMKisanStatusUseCase:
    pmkisan_repository: PMKisanRepository

    async def execute(self, request: PMKisanRequest) -> PMKisanResponse:
        if not request.mobile and not request.aadhaar and not request.registration_number:
            raise PMKisanValidationError("Mobile, Aadhaar or Registration number required")

        beneficiary = None
        if request.mobile:
            if len(request.mobile) != 10 or not request.mobile.isdigit():
                raise PMKisanValidationError("Mobile must be 10 digits")
            beneficiary = await self.pmkisan_repository.get_by_mobile(request.mobile)
        elif request.aadhaar:
            beneficiary = await self.pmkisan_repository.get_by_aadhaar(request.aadhaar)
        else:
            beneficiary = await self.pmkisan_repository.get_by_registration(request.registration_number)

        if not beneficiary:
            raise PMKisanNotFoundError("Beneficiary not found")

        installments = [
            InstallmentDTO(
                installment_number=i.installment_number,
                amount=i.amount,
                status=i.status.value,
                payment_date=i.payment_date.strftime("%Y-%m-%d") if i.payment_date else None,
                transaction_id=i.transaction_id
            )
            for i in beneficiary.installments
        ]

        return PMKisanResponse(
            registration_number=beneficiary.registration_number,
            name=beneficiary.name,
            father_name=beneficiary.father_name,
            mobile=beneficiary.mobile,
            state=beneficiary.state,
            district=beneficiary.district,
            block=beneficiary.block,
            village=beneficiary.village,
            aadhaar_linked=beneficiary.aadhaar_linked,
            total_received=beneficiary.total_received,
            pending_installments=beneficiary.pending_installments,
            installments=installments,
            last_payment_date=beneficiary.last_payment_date.strftime("%Y-%m-%d") if beneficiary.last_payment_date else None
        )
