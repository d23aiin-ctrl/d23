"""SIP Domain Entities."""
from dataclasses import dataclass

@dataclass
class SIPCalculation:
    monthly_investment: float
    duration_years: int
    expected_return_rate: float
    total_invested: float = 0
    estimated_returns: float = 0
    maturity_value: float = 0

    def calculate(self):
        n = self.duration_years * 12
        r = self.expected_return_rate / 12 / 100
        self.total_invested = self.monthly_investment * n
        if r > 0:
            self.maturity_value = self.monthly_investment * (((1+r)**n - 1) / r) * (1+r)
        else:
            self.maturity_value = self.total_invested
        self.estimated_returns = self.maturity_value - self.total_invested
        return self
