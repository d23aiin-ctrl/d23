"""E-Challan DTOs."""
from pydantic import BaseModel
from typing import List, Optional

class EChallanRequest(BaseModel):
    vehicle_number: Optional[str] = None
    challan_number: Optional[str] = None

class ViolationDTO(BaseModel):
    type: str
    description: str
    fine_amount: float

class EChallanResponse(BaseModel):
    success: bool = True
    challan_number: str
    challan_date: str
    vehicle_number: str
    location: str
    city: str
    state: str
    violations: List[ViolationDTO] = []
    total_fine: float
    status: str
    is_paid: bool
    is_overdue: bool
    due_date: Optional[str] = None
    payment_date: Optional[str] = None

class EChallanListResponse(BaseModel):
    success: bool = True
    vehicle_number: str
    total_challans: int
    pending_challans: int
    total_pending_amount: float
    challans: List[EChallanResponse] = []
