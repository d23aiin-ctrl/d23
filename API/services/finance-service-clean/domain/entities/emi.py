"""EMI Domain Entities."""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class LoanType(Enum):
    HOME = "Home Loan"
    CAR = "Car Loan"
    PERSONAL = "Personal Loan"
    EDUCATION = "Education Loan"

@dataclass
class EMIBreakdown:
    month: int
    emi: float
    principal: float
    interest: float
    balance: float

@dataclass
class EMICalculation:
    principal: float
    annual_rate: float
    tenure_months: int
    loan_type: LoanType
    monthly_emi: float = 0
    total_interest: float = 0
    total_amount: float = 0
    breakdown: List[EMIBreakdown] = field(default_factory=list)

    def calculate(self):
        r = self.annual_rate / 12 / 100
        n = self.tenure_months
        if r > 0:
            self.monthly_emi = self.principal * r * ((1+r)**n) / (((1+r)**n) - 1)
        else:
            self.monthly_emi = self.principal / n
        self.total_amount = self.monthly_emi * n
        self.total_interest = self.total_amount - self.principal
        return self
