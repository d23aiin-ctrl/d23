"""Vehicle DTOs."""
from pydantic import BaseModel
from typing import List, Optional

class VehicleRequest(BaseModel):
    registration_number: str

class OwnerDTO(BaseModel):
    name: str
    father_name: str
    address: str

class VehicleResponse(BaseModel):
    success: bool = True
    registration_number: str
    registration_date: str
    rto: str
    state: str
    make: str
    model: str
    vehicle_type: str
    fuel_type: str
    color: str
    engine_number: str
    chassis_number: str
    cubic_capacity: int
    seating_capacity: int
    owner: Optional[OwnerDTO] = None
    fitness_upto: Optional[str] = None
    tax_upto: Optional[str] = None
    insurance_upto: Optional[str] = None
    pucc_upto: Optional[str] = None
    is_financed: bool = False
    financer: Optional[str] = None
    is_blacklisted: bool = False
    pending_documents: List[str] = []
