"""
WhatsApp PM-KISAN Status Node.

Handles PM-KISAN beneficiary status queries for WhatsApp users.
"""

import logging
from typing import Dict, Any

from common.types import BotState
from common.tools.pmkisan_tool import (
    get_pmkisan_status,
    get_pmkisan_info,
    PMKISAN_SCHEME_INFO,
)

logger = logging.getLogger(__name__)


async def handle_pmkisan(state: BotState) -> BotState:
    """
    Handle PM-KISAN status requests.

    Args:
        state: Current bot state with user message and extracted entities

    Returns:
        Updated state with PM-KISAN response
    """
    detected_lang = state.get("detected_language", "en")
    entities = state.get("extracted_entities", {})

    # Extract identifiers from entities
    aadhaar = entities.get("aadhaar_number")
    mobile = entities.get("mobile_number")
    registration = entities.get("registration_number")

    logger.info(f"[PM-KISAN] Processing request - aadhaar: {bool(aadhaar)}, mobile: {bool(mobile)}, reg: {bool(registration)}")

    try:
        # Call the PM-KISAN tool
        result = await get_pmkisan_status(
            registration_number=registration,
            aadhaar_number=aadhaar,
            mobile_number=mobile,
        )

        if result.success:
            response = _format_pmkisan_response(result.data, detected_lang)
        else:
            response = _format_error_response(result.error, detected_lang)

        state["response_text"] = response
        state["response_type"] = "text"
        state["intent"] = "pmkisan_status"
        state["tool_result"] = result.data

    except Exception as e:
        logger.error(f"[PM-KISAN] Error: {e}", exc_info=True)
        state["response_text"] = _format_error_response(str(e), detected_lang)
        state["response_type"] = "text"
        state["intent"] = "pmkisan_status"
        state["error"] = str(e)

    return state


def _format_pmkisan_response(data: Dict[str, Any], lang: str) -> str:
    """Format PM-KISAN response for WhatsApp."""
    status = data.get("status", "info")

    if status == "otp_required":
        return _format_otp_required_response(data, lang)
    else:
        return _format_info_response(data, lang)


def _format_otp_required_response(data: Dict[str, Any], lang: str) -> str:
    """Format response when OTP verification is required."""
    how_to = data.get("how_to_check", {})
    scheme = data.get("scheme_info", PMKISAN_SCHEME_INFO)

    if lang == "hi":
        lines = [
            "🌾 *PM-KISAN स्थिति जांच*",
            "",
            "⚠️ PM-KISAN पोर्टल पर OTP वेरिफिकेशन जरूरी है।",
            "",
            "*स्थिति जांचने के लिए:*",
            f"1️⃣ {how_to.get('url', 'pmkisan.gov.in')} पर जाएं",
            f"2️⃣ अपना आधार/मोबाइल नंबर डालें",
            "3️⃣ OTP डालें",
            "4️⃣ भुगतान स्थिति देखें",
            "",
            "*योजना जानकारी:*",
            f"💰 लाभ: ₹6,000/वर्ष (₹2,000 × 3 किस्तें)",
            "",
            "*किस्तें:*",
            "• अप्रैल-जुलाई: ₹2,000",
            "• अगस्त-नवंबर: ₹2,000",
            "• दिसंबर-मार्च: ₹2,000",
            "",
            f"📞 हेल्पलाइन: {scheme.get('helpline', '155261')}",
        ]
    else:
        lines = [
            "🌾 *PM-KISAN Status Check*",
            "",
            "⚠️ OTP verification required on PM-KISAN portal.",
            "",
            "*How to check status:*",
            f"1️⃣ Visit {how_to.get('url', 'pmkisan.gov.in')}",
            f"2️⃣ Enter your Aadhaar/Mobile number",
            "3️⃣ Enter OTP received on your mobile",
            "4️⃣ View payment status",
            "",
            "*Scheme Information:*",
            f"💰 Benefit: ₹6,000/year (₹2,000 × 3 installments)",
            "",
            "*Installments:*",
            "• April-July: ₹2,000",
            "• August-November: ₹2,000",
            "• December-March: ₹2,000",
            "",
            f"📞 Helpline: {scheme.get('helpline', '155261')}",
        ]

    return "\n".join(lines)


def _format_info_response(data: Dict[str, Any], lang: str) -> str:
    """Format general scheme information response."""
    scheme = data.get("scheme_info", PMKISAN_SCHEME_INFO)
    how_to = data.get("how_to_check", {})

    if lang == "hi":
        lines = [
            "🌾 *PM-KISAN (प्रधानमंत्री किसान सम्मान निधि)*",
            "",
            "*लाभ:* ₹6,000 प्रति वर्ष",
            "   (₹2,000 की 3 किस्तों में)",
            "",
            "*पात्रता:*",
            "• सभी भूमिधारक किसान परिवार",
            "• आधार कार्ड आवश्यक",
            "• बैंक खाता आधार से लिंक होना चाहिए",
            "",
            "*आवश्यक दस्तावेज:*",
            "• आधार कार्ड",
            "• भूमि स्वामित्व दस्तावेज",
            "• बैंक खाता विवरण",
            "• मोबाइल नंबर (आधार से लिंक)",
            "",
            "*स्थिति जांचें:*",
            f"🔗 {scheme.get('status_check_url', 'pmkisan.gov.in')}",
            "",
            f"📞 हेल्पलाइन: {scheme.get('helpline', '155261')}",
            "",
            "_अपना आधार/मोबाइल नंबर भेजें स्थिति जानने के लिए_",
        ]
    else:
        lines = [
            "🌾 *PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)*",
            "",
            "*Benefit:* ₹6,000 per year",
            "   (In 3 installments of ₹2,000 each)",
            "",
            "*Eligibility:*",
            "• All landholding farmer families",
            "• Valid Aadhaar required",
            "• Bank account linked with Aadhaar",
            "",
            "*Documents Required:*",
            "• Aadhaar Card",
            "• Land ownership documents",
            "• Bank account details",
            "• Mobile number (linked with Aadhaar)",
            "",
            "*Check Status:*",
            f"🔗 {scheme.get('status_check_url', 'pmkisan.gov.in')}",
            "",
            f"📞 Helpline: {scheme.get('helpline', '155261')}",
            "",
            "_Send your Aadhaar/Mobile number to check status_",
        ]

    return "\n".join(lines)


def _format_error_response(error: str, lang: str) -> str:
    """Format error response."""
    if lang == "hi":
        return f"❌ PM-KISAN स्थिति जांचने में समस्या हुई। कृपया बाद में प्रयास करें।\n\n📞 हेल्पलाइन: 155261"
    else:
        return f"❌ Error checking PM-KISAN status. Please try again later.\n\n📞 Helpline: 155261"
