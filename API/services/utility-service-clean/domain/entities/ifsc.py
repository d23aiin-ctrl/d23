"""IFSC Domain Entities."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IFSCInfo:
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
