"""
CRSORGI (Civil Registration System) - Birth & Death Certificate Tool.

Provides information about birth and death certificate services
and portal access details.
"""

import logging
import re
from typing import Any, Dict, Optional

from common.graph.state import ToolResult

logger = logging.getLogger(__name__)

# CRSORGI Portal URLs
CRSORGI_BASE_URL = "https://crsorgi.gov.in"
CRSORGI_PORTAL_URL = "https://dc.crsorgi.gov.in/crs/"
BIHAR_CRS_URL = "https://crsorgi.gov.in/web/index.php/auth/login"

# Bihar Districts for CRS
BIHAR_DISTRICTS = [
    "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur",
    "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj",
    "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj",
    "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur",
    "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa",
    "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan",
    "Supaul", "Vaishali", "West Champaran",
]

# Certificate Information
BIRTH_CERTIFICATE_INFO = {
    "name": "Birth Certificate",
    "issuing_authority": "Registrar of Births and Deaths (Municipal/Panchayat)",
    "validity": "Lifetime (no expiry)",
    "uses": [
        "School admission",
        "Passport application",
        "Aadhaar enrollment",
        "Age verification",
        "Legal proceedings",
        "Government schemes",
    ],
    "registration_deadline": "21 days from date of birth (free), after that late fee applies",
    "documents_required": [
        "Hospital discharge certificate",
        "Parent's identity proof (Aadhaar/Voter ID)",
        "Parent's address proof",
        "Marriage certificate (if available)",
        "Affidavit (for late registration)",
    ],
    "fees": {
        "within_21_days": "Free",
        "21_days_to_1_year": "₹5 - ₹50 (varies by state)",
        "after_1_year": "₹10 - ₹100 + Court order may be required",
    },
}

DEATH_CERTIFICATE_INFO = {
    "name": "Death Certificate",
    "issuing_authority": "Registrar of Births and Deaths (Municipal/Panchayat)",
    "validity": "Lifetime (no expiry)",
    "uses": [
        "Insurance claim",
        "Property transfer",
        "Bank account settlement",
        "Pension claim",
        "Legal heir certificate",
        "Government records update",
    ],
    "registration_deadline": "21 days from date of death (free)",
    "documents_required": [
        "Hospital death certificate/Doctor's certificate",
        "Deceased's identity proof",
        "Informant's identity proof",
        "Address proof",
        "Affidavit (for late registration)",
    ],
    "fees": {
        "within_21_days": "Free",
        "21_days_to_1_year": "₹5 - ₹50",
        "after_1_year": "₹10 - ₹100 + Magistrate order required",
    },
}


def validate_registration_number(reg_no: str) -> bool:
    """Validate CRS registration number format."""
    if not reg_no:
        return False
    # Registration numbers vary by state/district
    cleaned = re.sub(r'[^A-Za-z0-9/\-]', '', reg_no)
    return len(cleaned) >= 5


def validate_year(year: str) -> Optional[int]:
    """Validate registration year."""
    try:
        year_int = int(year)
        if 1900 <= year_int <= 2100:
            return year_int
    except (ValueError, TypeError):
        pass
    return None


async def get_birth_certificate_info(
    registration_number: Optional[str] = None,
    year: Optional[str] = None,
    district: Optional[str] = None,
) -> ToolResult:
    """
    Get birth certificate information and status check instructions.

    Args:
        registration_number: Birth registration number
        year: Year of registration
        district: District name

    Returns:
        ToolResult with certificate information
    """
    data = {
        "certificate_type": "birth",
        "info": BIRTH_CERTIFICATE_INFO,
    }

    # Add search details if provided
    if registration_number and validate_registration_number(registration_number):
        data["registration_number"] = registration_number
        data["search_available"] = True
    else:
        data["search_available"] = False

    if year:
        validated_year = validate_year(year)
        if validated_year:
            data["year"] = validated_year

    if district:
        # Match district name (case-insensitive)
        matched_district = None
        for d in BIHAR_DISTRICTS:
            if d.lower() == district.lower() or d.lower() in district.lower():
                matched_district = d
                break
        if matched_district:
            data["district"] = matched_district

    # Build instructions
    data["how_to_get"] = {
        "online": {
            "url": CRSORGI_PORTAL_URL,
            "steps": [
                f"Visit {CRSORGI_PORTAL_URL}",
                "Select State: Bihar",
                f"Select District: {data.get('district', 'Your District')}",
                "Click on 'Birth Certificate'",
                "Enter registration details",
                "Download/Print certificate",
            ],
        },
        "offline": {
            "visit": "Municipal Corporation / Nagar Parishad / Gram Panchayat office",
            "documents": BIRTH_CERTIFICATE_INFO["documents_required"],
            "timeline": "3-7 working days",
        },
    }

    data["helpline"] = {
        "national": "011-23061373",
        "bihar_state": "0612-2506823",
        "portal": CRSORGI_PORTAL_URL,
    }

    return ToolResult(
        success=True,
        data=data,
        tool_name="birth_certificate",
    )


async def get_death_certificate_info(
    registration_number: Optional[str] = None,
    year: Optional[str] = None,
    district: Optional[str] = None,
) -> ToolResult:
    """
    Get death certificate information and status check instructions.

    Args:
        registration_number: Death registration number
        year: Year of registration
        district: District name

    Returns:
        ToolResult with certificate information
    """
    data = {
        "certificate_type": "death",
        "info": DEATH_CERTIFICATE_INFO,
    }

    # Add search details if provided
    if registration_number and validate_registration_number(registration_number):
        data["registration_number"] = registration_number
        data["search_available"] = True
    else:
        data["search_available"] = False

    if year:
        validated_year = validate_year(year)
        if validated_year:
            data["year"] = validated_year

    if district:
        # Match district name
        matched_district = None
        for d in BIHAR_DISTRICTS:
            if d.lower() == district.lower() or d.lower() in district.lower():
                matched_district = d
                break
        if matched_district:
            data["district"] = matched_district

    # Build instructions
    data["how_to_get"] = {
        "online": {
            "url": CRSORGI_PORTAL_URL,
            "steps": [
                f"Visit {CRSORGI_PORTAL_URL}",
                "Select State: Bihar",
                f"Select District: {data.get('district', 'Your District')}",
                "Click on 'Death Certificate'",
                "Enter registration details",
                "Download/Print certificate",
            ],
        },
        "offline": {
            "visit": "Municipal Corporation / Nagar Parishad / Gram Panchayat office",
            "documents": DEATH_CERTIFICATE_INFO["documents_required"],
            "timeline": "3-7 working days",
        },
    }

    data["helpline"] = {
        "national": "011-23061373",
        "bihar_state": "0612-2506823",
        "portal": CRSORGI_PORTAL_URL,
    }

    return ToolResult(
        success=True,
        data=data,
        tool_name="death_certificate",
    )


async def get_certificate_status(
    certificate_type: str,
    registration_number: str,
    year: Optional[str] = None,
    district: Optional[str] = None,
) -> ToolResult:
    """
    Get certificate status/download instructions.

    Args:
        certificate_type: "birth" or "death"
        registration_number: Registration number
        year: Year of registration
        district: District name

    Returns:
        ToolResult with status check instructions
    """
    if certificate_type.lower() not in ["birth", "death"]:
        return ToolResult(
            success=False,
            error="Certificate type must be 'birth' or 'death'",
            tool_name="certificate_status",
        )

    if not validate_registration_number(registration_number):
        return ToolResult(
            success=False,
            error="Invalid registration number format",
            tool_name="certificate_status",
        )

    cert_info = BIRTH_CERTIFICATE_INFO if certificate_type.lower() == "birth" else DEATH_CERTIFICATE_INFO

    return ToolResult(
        success=True,
        data={
            "certificate_type": certificate_type.lower(),
            "registration_number": registration_number,
            "year": validate_year(year) if year else None,
            "status": "manual_verification_required",
            "message": f"Please verify your {certificate_type} certificate status on the CRSORGI portal",
            "how_to_check": {
                "url": CRSORGI_PORTAL_URL,
                "steps": [
                    f"Visit {CRSORGI_PORTAL_URL}",
                    "Select State: Bihar",
                    f"Select District: {district or 'Your District'}",
                    f"Select Certificate Type: {certificate_type.title()}",
                    f"Enter Registration Number: {registration_number}",
                    f"Enter Year: {year or 'Registration Year'}",
                    "Click 'Search' to view/download certificate",
                ],
            },
            "certificate_info": cert_info,
            "helpline": {
                "national": "011-23061373",
                "portal": CRSORGI_PORTAL_URL,
            },
        },
        tool_name="certificate_status",
    )


def get_bihar_districts() -> list:
    """Get list of Bihar districts for CRS."""
    return BIHAR_DISTRICTS


def get_crs_info() -> Dict[str, Any]:
    """Get general CRS information."""
    return {
        "portal": CRSORGI_PORTAL_URL,
        "services": ["Birth Certificate", "Death Certificate", "Still Birth Certificate"],
        "states_covered": "All States and Union Territories of India",
        "bihar_districts": BIHAR_DISTRICTS,
        "birth_info": BIRTH_CERTIFICATE_INFO,
        "death_info": DEATH_CERTIFICATE_INFO,
        "helpline": "011-23061373",
    }
