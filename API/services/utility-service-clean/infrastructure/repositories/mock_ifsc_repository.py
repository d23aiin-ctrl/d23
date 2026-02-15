"""Mock IFSC Repository Implementation."""
from typing import Optional
from domain.entities import IFSCInfo
from domain.repositories import IFSCRepository


class MockIFSCRepository(IFSCRepository):
    """Mock implementation of IFSC repository for testing."""

    def __init__(self):
        self._ifsc_data = {
            "SBIN0001234": IFSCInfo(
                ifsc="SBIN0001234",
                bank_name="State Bank of India",
                branch="Connaught Place",
                address="A-Block, Connaught Place, New Delhi - 110001",
                city="New Delhi",
                district="Central Delhi",
                state="Delhi",
                contact="011-23456789",
                upi=True,
                rtgs=True,
                neft=True,
                imps=True,
                micr="110002001"
            ),
            "HDFC0000001": IFSCInfo(
                ifsc="HDFC0000001",
                bank_name="HDFC Bank",
                branch="Sandoz House",
                address="Dr Annie Besant Road, Worli, Mumbai - 400018",
                city="Mumbai",
                district="Mumbai",
                state="Maharashtra",
                contact="022-12345678",
                upi=True,
                rtgs=True,
                neft=True,
                imps=True,
                micr="400240001"
            ),
            "ICIC0000001": IFSCInfo(
                ifsc="ICIC0000001",
                bank_name="ICICI Bank",
                branch="Bandra Kurla Complex",
                address="ICICI Bank Towers, BKC, Mumbai - 400051",
                city="Mumbai",
                district="Mumbai",
                state="Maharashtra",
                contact="022-98765432",
                upi=True,
                rtgs=True,
                neft=True,
                imps=True,
                micr="400229001"
            ),
        }

    async def get_by_ifsc(self, ifsc: str) -> Optional[IFSCInfo]:
        return self._ifsc_data.get(ifsc.upper())
