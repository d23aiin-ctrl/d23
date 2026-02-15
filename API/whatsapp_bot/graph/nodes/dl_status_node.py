"""
WhatsApp Driving License Status Node.

Handles DL application status and vehicle RC queries for WhatsApp users.
"""

import logging
from typing import Dict, Any

from common.types import BotState
from common.tools.parivahan_tool import (
    get_dl_application_status,
    get_vehicle_rc_status,
    get_dl_info,
    get_bihar_rto_list,
    BIHAR_RTO_CODES,
)

logger = logging.getLogger(__name__)


async def handle_dl_status(state: BotState) -> BotState:
    """
    Handle driving license status requests.

    Args:
        state: Current bot state with user message and extracted entities

    Returns:
        Updated state with DL status response
    """
    detected_lang = state.get("detected_language", "en")
    entities = state.get("extracted_entities", {})
    message = state.get("whatsapp_message", {}).get("body", "").lower()

    # Extract identifiers
    application_number = entities.get("application_number") or entities.get("dl_application_number")
    dob = entities.get("date_of_birth") or entities.get("dob")
    vehicle_number = entities.get("vehicle_number")
    dl_number = entities.get("dl_number") or entities.get("driving_license_number")

    logger.info(f"[DL Status] Processing - app_no: {bool(application_number)}, dob: {bool(dob)}, vehicle: {bool(vehicle_number)}")

    try:
        # Determine query type
        if vehicle_number:
            # Vehicle RC status query
            result = await get_vehicle_rc_status(vehicle_number=vehicle_number)
            response = _format_rc_response(result.data, detected_lang)
        elif application_number and dob:
            # DL application status query
            result = await get_dl_application_status(application_number, dob)
            response = _format_dl_status_response(result.data, detected_lang)
        elif application_number:
            # Application number without DOB
            response = _request_dob_response(application_number, detected_lang)
            state["response_text"] = response
            state["response_type"] = "text"
            state["intent"] = "dl_status"
            state["awaiting"] = "date_of_birth"
            return state
        else:
            # General DL information
            response = _format_dl_info_response(detected_lang)

        state["response_text"] = response
        state["response_type"] = "text"
        state["intent"] = "dl_status"
        state["tool_result"] = result.data if 'result' in dir() else None

    except Exception as e:
        logger.error(f"[DL Status] Error: {e}", exc_info=True)
        state["response_text"] = _format_error_response(str(e), detected_lang)
        state["response_type"] = "text"
        state["intent"] = "dl_status"
        state["error"] = str(e)

    return state


def _format_dl_status_response(data: Dict[str, Any], lang: str) -> str:
    """Format DL application status response."""
    status = data.get("status", "manual_check_required")
    how_to = data.get("how_to_check", {})
    app_no = data.get("application_number", "")

    if lang == "hi":
        lines = [
            "🚗 *ड्राइविंग लाइसेंस स्थिति*",
            "",
            f"📋 आवेदन संख्या: {app_no}",
            "",
        ]

        if status == "captcha_required":
            lines.extend([
                "⚠️ पोर्टल पर CAPTCHA वेरिफिकेशन जरूरी है।",
                "",
                "*स्थिति जांचने के लिए:*",
                f"1️⃣ {how_to.get('url', 'parivahan.gov.in')} पर जाएं",
                f"2️⃣ आवेदन संख्या: {how_to.get('step2', app_no)}",
                "3️⃣ जन्मतिथि डालें",
                "4️⃣ CAPTCHA डालें और सबमिट करें",
            ])
        else:
            lines.extend([
                "*स्थिति जांचने के लिए:*",
                f"1️⃣ {how_to.get('url', 'parivahan.gov.in')} पर जाएं",
                "2️⃣ अपना विवरण डालें",
                "3️⃣ स्थिति देखें",
            ])

        lines.extend([
            "",
            "*संभावित स्थितियां:*",
            "• आवेदन जमा",
            "• प्रोसेसिंग में",
            "• टेस्ट शेड्यूल",
            "• टेस्ट पास",
            "• DL डिस्पैच के लिए तैयार",
            "• DL भेज दिया गया",
            "",
            f"📞 हेल्पलाइन: {data.get('helpline', '1800-120-0124')}",
        ])
    else:
        lines = [
            "🚗 *Driving License Status*",
            "",
            f"📋 Application No: {app_no}",
            "",
        ]

        if status == "captcha_required":
            lines.extend([
                "⚠️ CAPTCHA verification required on portal.",
                "",
                "*How to check status:*",
                f"1️⃣ Visit {how_to.get('url', 'parivahan.gov.in')}",
                f"2️⃣ Enter Application No: {app_no}",
                "3️⃣ Enter Date of Birth",
                "4️⃣ Enter CAPTCHA and submit",
            ])
        else:
            lines.extend([
                "*How to check status:*",
                f"1️⃣ Visit {how_to.get('url', 'parivahan.gov.in')}",
                "2️⃣ Enter your details",
                "3️⃣ View status",
            ])

        lines.extend([
            "",
            "*Possible Statuses:*",
            "• Application Submitted",
            "• Under Process",
            "• Test Scheduled",
            "• Test Passed",
            "• DL Ready for Dispatch",
            "• DL Dispatched",
            "",
            f"📞 Helpline: {data.get('helpline', '1800-120-0124')} (Toll Free)",
        ])

    return "\n".join(lines)


def _format_rc_response(data: Dict[str, Any], lang: str) -> str:
    """Format vehicle RC status response."""
    how_to = data.get("how_to_check", {})
    vehicle = data.get("search_value", "")
    rto_info = data.get("rto_info", "")

    if lang == "hi":
        lines = [
            "🚗 *वाहन RC स्थिति*",
            "",
            f"📋 वाहन नंबर: {vehicle}",
        ]

        if rto_info:
            lines.append(f"🏢 RTO: {rto_info}")

        lines.extend([
            "",
            "⚠️ पोर्टल पर CAPTCHA वेरिफिकेशन जरूरी है।",
            "",
            "*RC जांचने के लिए:*",
            f"1️⃣ {how_to.get('url', 'parivahan.gov.in')} पर जाएं",
            f"2️⃣ वाहन नंबर डालें: {vehicle}",
            "3️⃣ CAPTCHA डालें और सबमिट करें",
            "",
            f"📞 हेल्पलाइन: {data.get('helpline', '1800-120-0124')}",
        ])
    else:
        lines = [
            "🚗 *Vehicle RC Status*",
            "",
            f"📋 Vehicle Number: {vehicle}",
        ]

        if rto_info:
            lines.append(f"🏢 RTO: {rto_info}")

        lines.extend([
            "",
            "⚠️ CAPTCHA verification required on portal.",
            "",
            "*How to check RC:*",
            f"1️⃣ Visit {how_to.get('url', 'parivahan.gov.in')}",
            f"2️⃣ Enter Vehicle Number: {vehicle}",
            "3️⃣ Enter CAPTCHA and submit",
            "",
            f"📞 Helpline: {data.get('helpline', '1800-120-0124')} (Toll Free)",
        ])

    return "\n".join(lines)


def _request_dob_response(app_no: str, lang: str) -> str:
    """Ask user for date of birth."""
    if lang == "hi":
        return f"🚗 *DL स्थिति जांच*\n\n📋 आवेदन संख्या: {app_no}\n\n📅 कृपया अपनी जन्मतिथि भेजें (DD-MM-YYYY फॉर्मेट में)\n\nउदाहरण: 15-08-1990"
    else:
        return f"🚗 *DL Status Check*\n\n📋 Application No: {app_no}\n\n📅 Please send your date of birth (DD-MM-YYYY format)\n\nExample: 15-08-1990"


def _format_dl_info_response(lang: str) -> str:
    """Format general DL information."""
    dl_info = get_dl_info()

    if lang == "hi":
        lines = [
            "🚗 *ड्राइविंग लाइसेंस सेवाएं*",
            "",
            "*उपलब्ध सेवाएं:*",
            "• नया DL आवेदन",
            "• DL नवीनीकरण",
            "• डुप्लीकेट DL",
            "• पता बदलाव",
            "• अंतर्राष्ट्रीय ड्राइविंग परमिट",
            "",
            "*फीस:*",
            "• लर्निंग लाइसेंस: ₹200",
            "• स्थायी DL: ₹400",
            "• नवीनीकरण: ₹400",
            "• डुप्लीकेट: ₹400",
            "",
            "*वैधता:*",
            "• लर्निंग: 6 महीने",
            "• स्थायी: 20 साल या 50 वर्ष की आयु तक",
            "",
            "*आवश्यक दस्तावेज:*",
            "• आयु प्रमाण",
            "• पता प्रमाण (आधार/वोटर ID)",
            "• पासपोर्ट साइज फोटो",
            "• मेडिकल सर्टिफिकेट",
            "",
            "*स्थिति जांचें:*",
            "🔗 parivahan.gov.in",
            "",
            f"📞 हेल्पलाइन: 1800-120-0124",
            "",
            "_अपना आवेदन नंबर और जन्मतिथि भेजें स्थिति जानने के लिए_",
        ]
    else:
        lines = [
            "🚗 *Driving License Services*",
            "",
            "*Available Services:*",
            "• New DL Application",
            "• DL Renewal",
            "• Duplicate DL",
            "• Address Change",
            "• International Driving Permit",
            "",
            "*Fees:*",
            "• Learner's License: ₹200",
            "• Permanent DL: ₹400",
            "• Renewal: ₹400",
            "• Duplicate: ₹400",
            "",
            "*Validity:*",
            "• Learner's: 6 months",
            "• Permanent: 20 years or until age 50",
            "",
            "*Documents Required:*",
            "• Age proof",
            "• Address proof (Aadhaar/Voter ID)",
            "• Passport size photo",
            "• Medical certificate",
            "",
            "*Check Status:*",
            "🔗 parivahan.gov.in",
            "",
            f"📞 Helpline: 1800-120-0124 (Toll Free)",
            "",
            "_Send your application number and DOB to check status_",
        ]

    return "\n".join(lines)


def _format_error_response(error: str, lang: str) -> str:
    """Format error response."""
    if lang == "hi":
        return "❌ DL स्थिति जांचने में समस्या हुई। कृपया बाद में प्रयास करें।\n\n📞 हेल्पलाइन: 1800-120-0124"
    else:
        return "❌ Error checking DL status. Please try again later.\n\n📞 Helpline: 1800-120-0124"
