"""Mock PM-KISAN Repository."""
from typing import Optional
from datetime import date
from domain.repositories import PMKisanRepository
from domain.entities import PMKisanBeneficiary, PMKisanInstallment, InstallmentStatus

class MockPMKisanRepository(PMKisanRepository):
    def __init__(self):
        self._beneficiaries = {
            "9876543210": PMKisanBeneficiary(
                registration_number="PMKISAN123456",
                name="Ramesh Kumar",
                father_name="Suresh Kumar",
                mobile="9876543210",
                state="Uttar Pradesh",
                district="Varanasi",
                block="Chiraigaon",
                village="Kashi Nagar",
                aadhaar_linked=True,
                bank_account="1234567890",
                ifsc_code="SBIN0001234",
                registration_date=date(2020, 5, 15),
                installments=[
                    PMKisanInstallment(1, 2000, InstallmentStatus.PAID, date(2020, 8, 1), "TXN001"),
                    PMKisanInstallment(2, 2000, InstallmentStatus.PAID, date(2020, 12, 1), "TXN002"),
                    PMKisanInstallment(3, 2000, InstallmentStatus.PAID, date(2021, 4, 1), "TXN003"),
                    PMKisanInstallment(4, 2000, InstallmentStatus.PAID, date(2021, 8, 1), "TXN004"),
                    PMKisanInstallment(5, 2000, InstallmentStatus.PENDING),
                ]
            )
        }

    async def get_by_mobile(self, mobile: str) -> Optional[PMKisanBeneficiary]:
        return self._beneficiaries.get(mobile)

    async def get_by_aadhaar(self, aadhaar: str) -> Optional[PMKisanBeneficiary]:
        for b in self._beneficiaries.values():
            if hasattr(b, 'aadhaar') and b.aadhaar == aadhaar:
                return b
        return list(self._beneficiaries.values())[0] if aadhaar == "123456789012" else None

    async def get_by_registration(self, registration_number: str) -> Optional[PMKisanBeneficiary]:
        for b in self._beneficiaries.values():
            if b.registration_number == registration_number:
                return b
        return None
