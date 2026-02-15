"""
PM-KISAN Domain Entities.

Pradhan Mantri Kisan Samman Nidhi beneficiary data.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from enum import Enum


class InstallmentStatus(Enum):
    """Status of an installment."""
    PAID = "Paid"
    PENDING = "Pending"
    FAILED = "Failed"


@dataclass
class PMKisanInstallment:
    """Single installment payment."""
    installment_number: int
    amount: float
    status: InstallmentStatus
    payment_date: Optional[date] = None
    transaction_id: Optional[str] = None

    @property
    def is_paid(self) -> bool:
        return self.status == InstallmentStatus.PAID


@dataclass
class PMKisanBeneficiary:
    """
    PM-KISAN beneficiary entity.

    Contains farmer registration and payment details.
    """
    registration_number: str
    name: str
    father_name: str
    mobile: str
    state: str
    district: str
    block: str
    village: str
    aadhaar_linked: bool = True
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    installments: List[PMKisanInstallment] = field(default_factory=list)
    registration_date: Optional[date] = None

    @property
    def total_received(self) -> float:
        """Total amount received."""
        return sum(i.amount for i in self.installments if i.is_paid)

    @property
    def pending_installments(self) -> int:
        """Number of pending installments."""
        return sum(1 for i in self.installments if not i.is_paid)

    @property
    def last_payment_date(self) -> Optional[date]:
        """Date of last payment."""
        paid = [i for i in self.installments if i.is_paid and i.payment_date]
        if paid:
            return max(i.payment_date for i in paid)
        return None

    def validate(self) -> List[str]:
        """Validate beneficiary data."""
        errors = []
        if not self.registration_number:
            errors.append("Registration number required")
        if not self.mobile or len(self.mobile) != 10:
            errors.append("Valid 10-digit mobile required")
        return errors
