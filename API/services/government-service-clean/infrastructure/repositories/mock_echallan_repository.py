"""Mock E-Challan Repository."""
from typing import Optional, List
from datetime import date, datetime
from domain.repositories import EChallanRepository
from domain.entities import EChallan, Violation, ViolationType, ChallanStatus

class MockEChallanRepository(EChallanRepository):
    def __init__(self):
        self._challans = [
            EChallan(
                challan_number="ECHL2024001234",
                challan_date=datetime(2024, 10, 15, 14, 30),
                vehicle_number="DL01AB1234",
                location="ITO Junction",
                city="New Delhi",
                state="Delhi",
                violations=[
                    Violation(ViolationType.SIGNAL_JUMP, 1000),
                    Violation(ViolationType.NO_SEATBELT, 500)
                ],
                status=ChallanStatus.PENDING,
                due_date=date(2024, 11, 15)
            ),
            EChallan(
                challan_number="ECHL2024001235",
                challan_date=datetime(2024, 8, 10, 10, 15),
                vehicle_number="DL01AB1234",
                location="Connaught Place",
                city="New Delhi",
                state="Delhi",
                violations=[
                    Violation(ViolationType.WRONG_PARKING, 500)
                ],
                status=ChallanStatus.PAID,
                payment_date=date(2024, 8, 15),
                payment_reference="PAY123456"
            )
        ]

    async def get_by_vehicle(self, vehicle_number: str) -> List[EChallan]:
        return [c for c in self._challans if c.vehicle_number == vehicle_number]

    async def get_by_challan_number(self, challan_number: str) -> Optional[EChallan]:
        for c in self._challans:
            if c.challan_number == challan_number:
                return c
        return None

    async def get_pending(self, vehicle_number: str) -> List[EChallan]:
        return [c for c in self._challans if c.vehicle_number == vehicle_number and not c.is_paid]
