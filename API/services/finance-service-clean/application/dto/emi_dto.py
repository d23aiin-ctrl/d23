"""EMI DTOs."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class LoanTypeDTO(str, Enum):
    HOME = "home"
    CAR = "car"
    PERSONAL = "personal"
    EDUCATION = "education"


class EMIBreakdownDTO(BaseModel):
    month: int
    emi: float
    principal: float
    interest: float
    balance: float


class EMIRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan principal amount")
    annual_rate: float = Field(..., ge=0, le=50, description="Annual interest rate percentage")
    tenure_months: int = Field(..., gt=0, le=360, description="Loan tenure in months")
    loan_type: LoanTypeDTO = LoanTypeDTO.PERSONAL


class EMIResponse(BaseModel):
    success: bool = True
    principal: float
    annual_rate: float
    tenure_months: int
    loan_type: str
    monthly_emi: float
    total_interest: float
    total_amount: float
    breakdown: Optional[List[EMIBreakdownDTO]] = None
