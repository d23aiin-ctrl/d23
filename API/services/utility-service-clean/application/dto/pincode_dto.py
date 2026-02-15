"""Pincode DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List


class PincodeRequest(BaseModel):
    pincode: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class PincodeInfoDTO(BaseModel):
    pincode: str
    post_office: str
    district: str
    state: str
    country: str = "India"
    delivery_status: str
    division: Optional[str] = None
    region: Optional[str] = None


class PincodeResponse(BaseModel):
    success: bool = True
    data: Optional[List[PincodeInfoDTO]] = None
    error: Optional[str] = None
