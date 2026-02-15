"""Mock Vehicle Repository."""
from typing import Optional
from datetime import date
from domain.repositories import VehicleRepository
from domain.entities import VehicleRC, VehicleOwner, FuelType, VehicleType

class MockVehicleRepository(VehicleRepository):
    def __init__(self):
        self._vehicles = {
            "DL01AB1234": VehicleRC(
                registration_number="DL01AB1234",
                registration_date=date(2020, 6, 15),
                rto_code="DL01",
                rto_name="Delhi Central",
                state="Delhi",
                make="Maruti Suzuki",
                model="Swift VXI",
                vehicle_type=VehicleType.FOUR_WHEELER,
                fuel_type=FuelType.PETROL,
                color="White",
                engine_number="K12MN1234567",
                chassis_number="MA3EYD81S00123456",
                cubic_capacity=1197,
                seating_capacity=5,
                owner=VehicleOwner("Amit Sharma", "Rajesh Sharma", "123 Dwarka, Delhi"),
                fitness_upto=date(2035, 6, 14),
                tax_upto=date(2025, 6, 14),
                insurance_upto=date(2025, 6, 14),
                pucc_upto=date(2024, 12, 31),
                is_financed=True,
                financer_name="HDFC Bank"
            )
        }

    async def get_by_registration(self, registration_number: str) -> Optional[VehicleRC]:
        return self._vehicles.get(registration_number.upper().replace(" ", "").replace("-", ""))

    async def get_by_chassis(self, chassis_number: str) -> Optional[VehicleRC]:
        for v in self._vehicles.values():
            if v.chassis_number == chassis_number:
                return v
        return None
