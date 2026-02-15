"""Mock Pincode Repository Implementation."""
from typing import List, Optional
from domain.entities import PincodeInfo
from domain.repositories import PincodeRepository


class MockPincodeRepository(PincodeRepository):
    """Mock implementation of pincode repository for testing."""

    def __init__(self):
        self._pincodes = {
            "110001": [
                PincodeInfo(
                    pincode="110001",
                    post_office="Connaught Place",
                    district="Central Delhi",
                    state="Delhi",
                    delivery_status="Delivery",
                    division="New Delhi",
                    region="Delhi"
                ),
                PincodeInfo(
                    pincode="110001",
                    post_office="Parliament Street",
                    district="Central Delhi",
                    state="Delhi",
                    delivery_status="Delivery",
                    division="New Delhi",
                    region="Delhi"
                ),
            ],
            "400001": [
                PincodeInfo(
                    pincode="400001",
                    post_office="GPO Mumbai",
                    district="Mumbai",
                    state="Maharashtra",
                    delivery_status="Delivery",
                    division="Mumbai",
                    region="Western"
                ),
            ],
            "560001": [
                PincodeInfo(
                    pincode="560001",
                    post_office="GPO Bangalore",
                    district="Bangalore",
                    state="Karnataka",
                    delivery_status="Delivery",
                    division="Bangalore",
                    region="Southern"
                ),
            ],
        }

    async def get_by_pincode(self, pincode: str) -> List[PincodeInfo]:
        return self._pincodes.get(pincode, [])

    async def search_by_area(self, area: str, state: Optional[str] = None) -> List[PincodeInfo]:
        results = []
        area_lower = area.lower()
        for infos in self._pincodes.values():
            for info in infos:
                if area_lower in info.post_office.lower() or area_lower in info.district.lower():
                    if state is None or info.state.lower() == state.lower():
                        results.append(info)
        return results
