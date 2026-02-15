"""SIP DTOs."""
from pydantic import BaseModel, Field


class SIPRequest(BaseModel):
    monthly_investment: float = Field(..., gt=0, description="Monthly SIP amount")
    duration_years: int = Field(..., gt=0, le=40, description="Investment duration in years")
    expected_return_rate: float = Field(..., ge=0, le=30, description="Expected annual return rate percentage")


class SIPResponse(BaseModel):
    success: bool = True
    monthly_investment: float
    duration_years: int
    expected_return_rate: float
    total_invested: float
    estimated_returns: float
    maturity_value: float
