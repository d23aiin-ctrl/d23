"""
PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Status Tool.

Provides information about PM-KISAN scheme and attempts to fetch beneficiary status.
Note: PM-KISAN portal requires OTP verification, so direct API access is limited.
"""

import logging
import re
from typing import Any, Dict, Optional

import httpx
from bs4 import BeautifulSoup

from common.graph.state import ToolResult

logger = logging.getLogger(__name__)

# PM-KISAN Portal URLs
PMKISAN_BASE_URL = "https://pmkisan.gov.in"
PMKISAN_STATUS_URL = f"{PMKISAN_BASE_URL}/beneficiarystatus_new.aspx"

# Scheme information
PMKISAN_SCHEME_INFO = {
    "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
    "benefit": "₹6,000 per year in 3 installments of ₹2,000 each",
    "eligibility": [
        "All landholding farmer families",
        "Subject to certain exclusion criteria",
        "Must have valid Aadhaar",
        "Bank account linked with Aadhaar",
    ],
    "installments": [
        {"number": 1, "period": "April-July", "amount": 2000},
        {"number": 2, "period": "August-November", "amount": 2000},
        {"number": 3, "period": "December-March", "amount": 2000},
    ],
    "documents_required": [
        "Aadhaar Card",
        "Land ownership documents",
        "Bank account details",
        "Mobile number linked with Aadhaar",
    ],
    "portal_url": "https://pmkisan.gov.in/",
    "status_check_url": "https://pmkisan.gov.in/beneficiarystatus_new.aspx",
    "helpline": "155261 / 011-24300606",
}


def validate_aadhaar(aadhaar: str) -> bool:
    """Validate Aadhaar number format (12 digits)."""
    if not aadhaar:
        return False
    cleaned = re.sub(r'\D', '', aadhaar)
    return len(cleaned) == 12


def validate_mobile(mobile: str) -> bool:
    """Validate Indian mobile number (10 digits)."""
    if not mobile:
        return False
    cleaned = re.sub(r'\D', '', mobile)
    # Remove country code if present
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    return len(cleaned) == 10 and cleaned[0] in '6789'


def validate_registration_number(reg_no: str) -> bool:
    """Validate PM-KISAN registration number format."""
    if not reg_no:
        return False
    cleaned = re.sub(r'\D', '', reg_no)
    return len(cleaned) >= 10


async def get_pmkisan_status(
    registration_number: Optional[str] = None,
    aadhaar_number: Optional[str] = None,
    mobile_number: Optional[str] = None,
) -> ToolResult:
    """
    Get PM-KISAN beneficiary status.

    Note: Due to OTP verification requirements on the portal,
    direct status fetch may not always work. Falls back to
    providing scheme information and portal links.

    Args:
        registration_number: PM-KISAN registration number
        aadhaar_number: Aadhaar number (12 digits)
        mobile_number: Registered mobile number

    Returns:
        ToolResult with status information or scheme details
    """
    # Validate inputs
    has_valid_input = False
    search_method = None
    search_value = None

    if registration_number and validate_registration_number(registration_number):
        has_valid_input = True
        search_method = "registration"
        search_value = re.sub(r'\D', '', registration_number)
    elif aadhaar_number and validate_aadhaar(aadhaar_number):
        has_valid_input = True
        search_method = "aadhaar"
        search_value = re.sub(r'\D', '', aadhaar_number)
    elif mobile_number and validate_mobile(mobile_number):
        has_valid_input = True
        search_method = "mobile"
        search_value = re.sub(r'\D', '', mobile_number)
        if search_value.startswith('91') and len(search_value) == 12:
            search_value = search_value[2:]

    if not has_valid_input:
        # Return scheme information if no valid input
        return ToolResult(
            success=True,
            data={
                "status": "info",
                "message": "PM-KISAN scheme information",
                "scheme_info": PMKISAN_SCHEME_INFO,
                "how_to_check": {
                    "step1": "Visit " + PMKISAN_STATUS_URL,
                    "step2": "Enter your Aadhaar or mobile number",
                    "step3": "Enter OTP received on registered mobile",
                    "step4": "View your payment status",
                },
            },
            tool_name="pmkisan_status",
        )

    # Attempt to fetch status from portal
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, get the page to extract form tokens
            response = await client.get(
                PMKISAN_STATUS_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )

            if response.status_code != 200:
                raise Exception(f"Portal returned status {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract ASP.NET form tokens
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})

            if not all([viewstate, viewstate_gen, event_validation]):
                raise Exception("Could not extract form tokens")

            # Note: The actual status check requires OTP verification
            # which cannot be automated without user interaction.
            # Return information about how to check status manually.

            logger.info(f"PM-KISAN portal accessible, but OTP verification required")

            return ToolResult(
                success=True,
                data={
                    "status": "otp_required",
                    "message": "PM-KISAN status check requires OTP verification on your registered mobile",
                    "search_method": search_method,
                    "search_value_masked": search_value[:4] + "****" + search_value[-2:] if len(search_value) > 6 else "****",
                    "how_to_check": {
                        "url": PMKISAN_STATUS_URL,
                        "step1": f"Visit {PMKISAN_STATUS_URL}",
                        "step2": f"Select '{search_method}' option",
                        "step3": f"Enter your {search_method} number",
                        "step4": "Enter OTP received on your registered mobile",
                        "step5": "View your payment status and installment details",
                    },
                    "scheme_info": PMKISAN_SCHEME_INFO,
                    "helpline": PMKISAN_SCHEME_INFO["helpline"],
                },
                tool_name="pmkisan_status",
            )

    except Exception as e:
        logger.error(f"PM-KISAN status check error: {e}")

        # Return fallback information
        return ToolResult(
            success=True,
            data={
                "status": "fallback",
                "message": "Could not connect to PM-KISAN portal. Here's how to check manually:",
                "search_method": search_method,
                "how_to_check": {
                    "url": PMKISAN_STATUS_URL,
                    "step1": f"Visit {PMKISAN_STATUS_URL}",
                    "step2": f"Enter your {search_method} number",
                    "step3": "Complete OTP verification",
                    "step4": "View your payment status",
                },
                "scheme_info": PMKISAN_SCHEME_INFO,
                "helpline": PMKISAN_SCHEME_INFO["helpline"],
                "error": str(e),
            },
            tool_name="pmkisan_status",
        )


def get_pmkisan_info() -> Dict[str, Any]:
    """Get PM-KISAN scheme information."""
    return PMKISAN_SCHEME_INFO
