"""PM-KISAN DTOs."""
from pydantic import BaseModel, Field
from typing import List, Optional

class PMKisanRequest(BaseModel):
    mobile: Optional[str] = Field(None, min_length=10, max_length=10)
    aadhaar: Optional[str] = Field(None, min_length=12, max_length=12)
    registration_number: Optional[str] = None

class InstallmentDTO(BaseModel):
    installment_number: int
    amount: float
    status: str
    payment_date: Optional[str] = None
    transaction_id: Optional[str] = None

class PMKisanResponse(BaseModel):
    success: bool = True
    registration_number: str
    name: str
    father_name: str
    mobile: str
    state: str
    district: str
    block: str
    village: str
    aadhaar_linked: bool
    total_received: float
    pending_installments: int
    installments: List[InstallmentDTO] = []
    last_payment_date: Optional[str] = None
