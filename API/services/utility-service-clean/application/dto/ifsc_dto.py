"""IFSC DTOs."""
from pydantic import BaseModel, Field
from typing import Optional


class IFSCRequest(BaseModel):
    ifsc: str = Field(..., min_length=11, max_length=11, pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")


class IFSCInfoDTO(BaseModel):
    ifsc: str
    bank_name: str
    branch: str
    address: str
    city: str
    district: str
    state: str
    contact: Optional[str] = None
    upi: bool = True
    rtgs: bool = True
    neft: bool = True
    imps: bool = True
    micr: Optional[str] = None


class IFSCResponse(BaseModel):
    success: bool = True
    data: Optional[IFSCInfoDTO] = None
    error: Optional[str] = None
