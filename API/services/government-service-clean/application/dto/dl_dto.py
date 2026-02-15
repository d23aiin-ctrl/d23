"""Driving License DTOs."""
from pydantic import BaseModel, Field
from typing import List, Optional

class DLRequest(BaseModel):
    dl_number: str = Field(..., min_length=10)
    dob: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")

class VehicleClassDTO(BaseModel):
    code: str
    description: str
    issue_date: Optional[str] = None

class DLResponse(BaseModel):
    success: bool = True
    dl_number: str
    name: str
    father_name: str
    date_of_birth: str
    blood_group: Optional[str] = None
    address: str
    state: str
    rto_code: str
    issue_date: str
    validity_nt: str
    validity_trans: Optional[str] = None
    status: str
    is_valid: bool
    days_to_expiry: int
    vehicle_classes: List[VehicleClassDTO] = []
