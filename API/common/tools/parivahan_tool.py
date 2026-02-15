"""
Parivahan (Driving License & Vehicle Registration) Status Tool.

Provides DL application status check and vehicle RC information.
Uses web scraping from parivahan.gov.in portal.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from bs4 import BeautifulSoup

from common.graph.state import ToolResult

logger = logging.getLogger(__name__)

# Parivahan Portal URLs
PARIVAHAN_BASE_URL = "https://parivahan.gov.in"
DL_STATUS_URL = f"{PARIVAHAN_BASE_URL}/rcdlstatus/?pur_cd=101"
RC_STATUS_URL = f"{PARIVAHAN_BASE_URL}/rcdlstatus/?pur_cd=102"
SARATHI_URL = "https://sarathi.parivahan.gov.in"

# RTO Codes for Bihar
BIHAR_RTO_CODES = {
    "BR01": "Patna",
    "BR02": "Gaya",
    "BR03": "Muzaffarpur",
    "BR04": "Bhagalpur",
    "BR05": "Darbhanga",
    "BR06": "Purnia",
    "BR07": "Chhapra",
    "BR08": "Begusarai",
    "BR09": "Samastipur",
    "BR10": "Munger",
    "BR19": "Nalanda",
    "BR21": "Jehanabad",
    "BR22": "Nawada",
    "BR24": "Aurangabad",
    "BR25": "Rohtas",
    "BR26": "Buxar",
    "BR27": "Kaimur",
    "BR28": "Vaishali",
    "BR29": "East Champaran",
    "BR30": "West Champaran",
    "BR31": "Sitamarhi",
    "BR32": "Sheohar",
    "BR33": "Madhubani",
    "BR34": "Supaul",
    "BR35": "Araria",
    "BR36": "Kishanganj",
    "BR37": "Katihar",
    "BR38": "Khagaria",
    "BR39": "Saharsa",
    "BR40": "Madhepura",
    "BR43": "Lakhisarai",
    "BR44": "Sheikhpura",
    "BR50": "Patna City",
    "BR51": "Patna West",
    "BR52": "Saran",
    "BR53": "Siwan",
    "BR54": "Gopalganj",
    "BR55": "Jamui",
    "BR56": "Banka",
    "BR57": "Bhojpur",
    "BR58": "Arwal",
}


def validate_application_number(app_no: str) -> bool:
    """Validate DL application number format."""
    if not app_no:
        return False
    # Application numbers are usually alphanumeric, 10-20 chars
    cleaned = re.sub(r'[^A-Za-z0-9]', '', app_no)
    return 8 <= len(cleaned) <= 25


def validate_dob(dob: str) -> Optional[str]:
    """
    Validate and format date of birth.
    Returns formatted date (DD-MM-YYYY) or None if invalid.
    """
    if not dob:
        return None

    # Try different formats
    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d %m %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dob.strip(), fmt)
            return dt.strftime("%d-%m-%Y")
        except ValueError:
            continue

    return None


def validate_dl_number(dl_no: str) -> bool:
    """Validate driving license number format."""
    if not dl_no:
        return False
    # DL format: SS-RRYYYYYNNNNNN (state-rto-year-serial)
    # Example: BR-0120190012345
    cleaned = re.sub(r'[^A-Za-z0-9]', '', dl_no.upper())
    return 13 <= len(cleaned) <= 20


def validate_vehicle_number(veh_no: str) -> bool:
    """Validate vehicle registration number format."""
    if not veh_no:
        return False
    # Format: SS-NN-XX-NNNN (state-rto-series-number)
    cleaned = re.sub(r'[^A-Za-z0-9]', '', veh_no.upper())
    return 8 <= len(cleaned) <= 12


async def get_dl_application_status(
    application_number: str,
    date_of_birth: str,
) -> ToolResult:
    """
    Get driving license application status from Parivahan portal.

    Args:
        application_number: DL application number
        date_of_birth: Date of birth (DD-MM-YYYY or similar format)

    Returns:
        ToolResult with application status or error
    """
    # Validate inputs
    if not validate_application_number(application_number):
        return ToolResult(
            success=False,
            error="Invalid application number format. Please provide a valid DL application number.",
            tool_name="dl_status",
        )

    formatted_dob = validate_dob(date_of_birth)
    if not formatted_dob:
        return ToolResult(
            success=False,
            error="Invalid date of birth format. Please use DD-MM-YYYY format.",
            tool_name="dl_status",
        )

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # First, get the page to extract ASP.NET form tokens
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }

            response = await client.get(DL_STATUS_URL, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Portal returned status {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract ASP.NET form tokens
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})

            if not viewstate:
                # Portal structure may have changed or requires JavaScript
                logger.warning("Could not extract form tokens from Parivahan portal")

                return ToolResult(
                    success=True,
                    data={
                        "status": "manual_check_required",
                        "message": "Please check DL status manually on Parivahan portal",
                        "application_number": application_number,
                        "how_to_check": {
                            "url": DL_STATUS_URL,
                            "step1": f"Visit {DL_STATUS_URL}",
                            "step2": f"Enter Application Number: {application_number}",
                            "step3": f"Enter Date of Birth: {formatted_dob}",
                            "step4": "Enter CAPTCHA and submit",
                        },
                        "alternative_url": SARATHI_URL,
                        "helpline": "1800-120-0124 (Toll Free)",
                    },
                    tool_name="dl_status",
                )

            # Note: CAPTCHA verification is required, so we return instructions
            logger.info(f"DL status check requires CAPTCHA verification")

            return ToolResult(
                success=True,
                data={
                    "status": "captcha_required",
                    "message": "DL status check requires CAPTCHA verification on the portal",
                    "application_number": application_number,
                    "date_of_birth": formatted_dob,
                    "how_to_check": {
                        "url": DL_STATUS_URL,
                        "step1": f"Visit {DL_STATUS_URL}",
                        "step2": f"Enter Application Number: {application_number}",
                        "step3": f"Enter Date of Birth: {formatted_dob}",
                        "step4": "Enter CAPTCHA code shown on screen",
                        "step5": "Click 'Submit' to view status",
                    },
                    "expected_statuses": [
                        "Application Submitted",
                        "Under Process",
                        "Test Scheduled",
                        "Test Passed",
                        "DL Ready for Dispatch",
                        "DL Dispatched",
                    ],
                    "alternative_url": SARATHI_URL,
                    "helpline": "1800-120-0124 (Toll Free)",
                },
                tool_name="dl_status",
            )

    except httpx.TimeoutException:
        logger.error("Timeout connecting to Parivahan portal")
        return ToolResult(
            success=True,
            data={
                "status": "timeout",
                "message": "Parivahan portal is slow to respond. Please try again or check manually.",
                "how_to_check": {
                    "url": DL_STATUS_URL,
                    "application_number": application_number,
                },
                "helpline": "1800-120-0124 (Toll Free)",
            },
            tool_name="dl_status",
        )
    except Exception as e:
        logger.error(f"DL status check error: {e}")
        return ToolResult(
            success=True,
            data={
                "status": "error",
                "message": "Could not connect to Parivahan portal. Please check manually.",
                "how_to_check": {
                    "url": DL_STATUS_URL,
                    "application_number": application_number,
                },
                "error": str(e),
                "helpline": "1800-120-0124 (Toll Free)",
            },
            tool_name="dl_status",
        )


async def get_vehicle_rc_status(
    vehicle_number: Optional[str] = None,
    application_number: Optional[str] = None,
) -> ToolResult:
    """
    Get vehicle registration certificate (RC) status.

    Args:
        vehicle_number: Vehicle registration number (e.g., BR01AB1234)
        application_number: RC application number

    Returns:
        ToolResult with RC status or information
    """
    if vehicle_number and validate_vehicle_number(vehicle_number):
        search_value = re.sub(r'[^A-Za-z0-9]', '', vehicle_number.upper())
        search_type = "vehicle_number"
    elif application_number and validate_application_number(application_number):
        search_value = application_number.upper()
        search_type = "application_number"
    else:
        return ToolResult(
            success=False,
            error="Please provide a valid vehicle number (e.g., BR01AB1234) or application number.",
            tool_name="rc_status",
        )

    # Format vehicle number for display
    if search_type == "vehicle_number" and len(search_value) >= 10:
        formatted = f"{search_value[:4]}-{search_value[4:6]}-{search_value[6:]}"
    else:
        formatted = search_value

    return ToolResult(
        success=True,
        data={
            "status": "manual_check_required",
            "message": "RC status check requires verification on Parivahan portal",
            "search_type": search_type,
            "search_value": formatted,
            "how_to_check": {
                "url": RC_STATUS_URL,
                "step1": f"Visit {RC_STATUS_URL}",
                "step2": f"Enter {search_type.replace('_', ' ').title()}: {formatted}",
                "step3": "Enter CAPTCHA and submit",
            },
            "rto_info": BIHAR_RTO_CODES.get(search_value[:4], "Unknown RTO") if search_type == "vehicle_number" else None,
            "helpline": "1800-120-0124 (Toll Free)",
        },
        tool_name="rc_status",
    )


def get_bihar_rto_list() -> Dict[str, str]:
    """Get list of Bihar RTO codes and names."""
    return BIHAR_RTO_CODES


def get_dl_info() -> Dict[str, Any]:
    """Get general information about driving license services."""
    return {
        "services": {
            "new_dl": "Apply for new Driving License",
            "renewal": "Renew expired Driving License",
            "duplicate": "Get duplicate DL (lost/damaged)",
            "international": "Apply for International Driving Permit",
            "address_change": "Change address on DL",
        },
        "documents_required": [
            "Age proof (Birth certificate, School certificate)",
            "Address proof (Aadhaar, Voter ID, Passport)",
            "Passport size photographs",
            "Medical certificate (Form 1A)",
            "Learner's License (for permanent DL)",
        ],
        "fees": {
            "learners_license": "₹200",
            "permanent_dl": "₹400",
            "renewal": "₹400",
            "duplicate": "₹400",
            "international_permit": "₹1000",
        },
        "validity": {
            "learners": "6 months",
            "permanent": "20 years or until age 50 (whichever is earlier)",
            "above_50": "5 years",
        },
        "portals": {
            "status_check": DL_STATUS_URL,
            "online_apply": SARATHI_URL,
        },
        "helpline": "1800-120-0124 (Toll Free)",
    }
