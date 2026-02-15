"""Pincode Domain Entities."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PincodeInfo:
    pincode: str
    post_office: str
    district: str
    state: str
    country: str = "India"
    delivery_status: str = "Delivery"
    division: Optional[str] = None
    region: Optional[str] = None
    block: Optional[str] = None
    branch_type: Optional[str] = None
