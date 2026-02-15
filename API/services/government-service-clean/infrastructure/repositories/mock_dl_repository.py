"""Mock DL Repository."""
from typing import Optional
from datetime import date
from domain.repositories import DLRepository
from domain.entities import DrivingLicense, VehicleClass, DLStatus

class MockDLRepository(DLRepository):
    def __init__(self):
        self._licenses = {
            "DL0120160001234": DrivingLicense(
                dl_number="DL0120160001234",
                name="Amit Sharma",
                father_name="Rajesh Sharma",
                date_of_birth=date(1990, 5, 15),
                blood_group="B+",
                address="123, Sector 5, Dwarka, New Delhi",
                state="Delhi",
                rto_code="DL01",
                issue_date=date(2016, 3, 20),
                validity_nt=date(2036, 3, 19),
                validity_trans=date(2026, 3, 19),
                vehicle_classes=[VehicleClass.MCWG, VehicleClass.LMV],
                status=DLStatus.ACTIVE
            )
        }

    async def get_by_dl_number(self, dl_number: str) -> Optional[DrivingLicense]:
        return self._licenses.get(dl_number.upper())

    async def verify_dl(self, dl_number: str, dob: str) -> Optional[DrivingLicense]:
        dl = await self.get_by_dl_number(dl_number)
        if dl and dl.date_of_birth.strftime("%Y-%m-%d") == dob:
            return dl
        return None
