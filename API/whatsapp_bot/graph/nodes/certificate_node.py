"""
WhatsApp Birth/Death Certificate Node.

Handles birth and death certificate queries for WhatsApp users.
"""

import logging
from typing import Dict, Any

from common.types import BotState
from common.tools.crsorgi_tool import (
    get_birth_certificate_info,
    get_death_certificate_info,
    get_certificate_status,
    get_crs_info,
    BIRTH_CERTIFICATE_INFO,
    DEATH_CERTIFICATE_INFO,
)

logger = logging.getLogger(__name__)


async def handle_certificate(state: BotState) -> BotState:
    """
    Handle birth/death certificate requests.

    Args:
        state: Current bot state with user message and extracted entities

    Returns:
        Updated state with certificate response
    """
    detected_lang = state.get("detected_language", "en")
    entities = state.get("extracted_entities", {})
    message = state.get("whatsapp_message", {}).get("body", "").lower()

    # Determine certificate type from message
    cert_type = _detect_certificate_type(message, entities)

    # Extract identifiers
    registration_number = entities.get("registration_number")
    year = entities.get("year")
    district = entities.get("district")

    logger.info(f"[Certificate] Processing - type: {cert_type}, reg_no: {bool(registration_number)}, district: {district}")

    try:
        if cert_type == "birth":
            result = await get_birth_certificate_info(
                registration_number=registration_number,
                year=year,
                district=district,
            )
            response = _format_birth_certificate_response(result.data, detected_lang)
        elif cert_type == "death":
            result = await get_death_certificate_info(
                registration_number=registration_number,
                year=year,
                district=district,
            )
            response = _format_death_certificate_response(result.data, detected_lang)
        else:
            # General certificate information
            response = _format_general_info_response(detected_lang)

        state["response_text"] = response
        state["response_type"] = "text"
        state["intent"] = "certificate_status"
        state["tool_result"] = result.data if 'result' in dir() else None

    except Exception as e:
        logger.error(f"[Certificate] Error: {e}", exc_info=True)
        state["response_text"] = _format_error_response(str(e), detected_lang)
        state["response_type"] = "text"
        state["intent"] = "certificate_status"
        state["error"] = str(e)

    return state


def _detect_certificate_type(message: str, entities: Dict[str, Any]) -> str:
    """Detect certificate type from message."""
    # Check entities first
    cert_type = entities.get("certificate_type", "")
    if cert_type:
        return cert_type.lower()

    # Keywords for birth certificate
    birth_keywords = [
        "birth", "janm", "जन्म", "पैदाइश", "janam",
        "born", "birthday", "jnm",
    ]

    # Keywords for death certificate
    death_keywords = [
        "death", "mrityu", "मृत्यु", "मौत", "maut",
        "died", "deceased", "expire", "demise",
    ]

    message_lower = message.lower()

    for kw in death_keywords:
        if kw in message_lower:
            return "death"

    for kw in birth_keywords:
        if kw in message_lower:
            return "birth"

    return "general"


def _format_birth_certificate_response(data: Dict[str, Any], lang: str) -> str:
    """Format birth certificate response."""
    info = data.get("info", BIRTH_CERTIFICATE_INFO)
    how_to = data.get("how_to_get", {})
    helpline = data.get("helpline", {})
    district = data.get("district", "")

    if lang == "hi":
        lines = [
            "👶 *जन्म प्रमाण पत्र*",
            "",
            "*उपयोग:*",
            "• स्कूल में दाखिला",
            "• पासपोर्ट आवेदन",
            "• आधार नामांकन",
            "• आयु सत्यापन",
            "• सरकारी योजनाएं",
            "",
            "*पंजीकरण समय सीमा:*",
            "• 21 दिन के भीतर: निःशुल्क",
            "• 21 दिन - 1 वर्ष: ₹5-50",
            "• 1 वर्ष के बाद: ₹10-100 + कोर्ट ऑर्डर",
            "",
            "*आवश्यक दस्तावेज:*",
            "• अस्पताल डिस्चार्ज सर्टिफिकेट",
            "• माता-पिता का पहचान प्रमाण",
            "• पता प्रमाण",
            "• विवाह प्रमाण पत्र",
            "",
        ]

        # Online instructions
        online = how_to.get("online", {})
        lines.extend([
            "*ऑनलाइन प्राप्त करें:*",
            f"🔗 {online.get('url', 'dc.crsorgi.gov.in/crs/')}",
            "1. राज्य चुनें: बिहार",
            f"2. जिला चुनें: {district or 'अपना जिला'}",
            "3. जन्म प्रमाण पत्र चुनें",
            "4. पंजीकरण विवरण डालें",
            "",
            "*ऑफलाइन:*",
            "नगर निगम / नगर परिषद / ग्राम पंचायत कार्यालय जाएं",
            "",
            f"📞 हेल्पलाइन: {helpline.get('national', '011-23061373')}",
            f"📞 बिहार: {helpline.get('bihar_state', '0612-2506823')}",
        ])
    else:
        lines = [
            "👶 *Birth Certificate*",
            "",
            "*Uses:*",
            "• School admission",
            "• Passport application",
            "• Aadhaar enrollment",
            "• Age verification",
            "• Government schemes",
            "",
            "*Registration Deadline:*",
            "• Within 21 days: Free",
            "• 21 days - 1 year: ₹5-50",
            "• After 1 year: ₹10-100 + Court order may be required",
            "",
            "*Documents Required:*",
            "• Hospital discharge certificate",
            "• Parent's identity proof",
            "• Address proof",
            "• Marriage certificate",
            "",
        ]

        # Online instructions
        online = how_to.get("online", {})
        lines.extend([
            "*Get Online:*",
            f"🔗 {online.get('url', 'dc.crsorgi.gov.in/crs/')}",
            "1. Select State: Bihar",
            f"2. Select District: {district or 'Your District'}",
            "3. Choose Birth Certificate",
            "4. Enter registration details",
            "",
            "*Offline:*",
            "Visit Municipal Corporation / Nagar Parishad / Gram Panchayat office",
            "",
            f"📞 Helpline: {helpline.get('national', '011-23061373')}",
            f"📞 Bihar: {helpline.get('bihar_state', '0612-2506823')}",
        ])

    return "\n".join(lines)


def _format_death_certificate_response(data: Dict[str, Any], lang: str) -> str:
    """Format death certificate response."""
    info = data.get("info", DEATH_CERTIFICATE_INFO)
    how_to = data.get("how_to_get", {})
    helpline = data.get("helpline", {})
    district = data.get("district", "")

    if lang == "hi":
        lines = [
            "🕯️ *मृत्यु प्रमाण पत्र*",
            "",
            "*उपयोग:*",
            "• बीमा दावा",
            "• संपत्ति हस्तांतरण",
            "• बैंक खाता निपटान",
            "• पेंशन दावा",
            "• कानूनी उत्तराधिकारी प्रमाण पत्र",
            "",
            "*पंजीकरण समय सीमा:*",
            "• 21 दिन के भीतर: निःशुल्क",
            "• 21 दिन - 1 वर्ष: ₹5-50",
            "• 1 वर्ष के बाद: ₹10-100 + मजिस्ट्रेट ऑर्डर",
            "",
            "*आवश्यक दस्तावेज:*",
            "• अस्पताल मृत्यु प्रमाण पत्र",
            "• मृतक का पहचान प्रमाण",
            "• सूचना देने वाले का पहचान प्रमाण",
            "• पता प्रमाण",
            "",
        ]

        # Online instructions
        online = how_to.get("online", {})
        lines.extend([
            "*ऑनलाइन प्राप्त करें:*",
            f"🔗 {online.get('url', 'dc.crsorgi.gov.in/crs/')}",
            "1. राज्य चुनें: बिहार",
            f"2. जिला चुनें: {district or 'अपना जिला'}",
            "3. मृत्यु प्रमाण पत्र चुनें",
            "4. पंजीकरण विवरण डालें",
            "",
            "*ऑफलाइन:*",
            "नगर निगम / नगर परिषद / ग्राम पंचायत कार्यालय जाएं",
            "",
            f"📞 हेल्पलाइन: {helpline.get('national', '011-23061373')}",
            f"📞 बिहार: {helpline.get('bihar_state', '0612-2506823')}",
        ])
    else:
        lines = [
            "🕯️ *Death Certificate*",
            "",
            "*Uses:*",
            "• Insurance claim",
            "• Property transfer",
            "• Bank account settlement",
            "• Pension claim",
            "• Legal heir certificate",
            "",
            "*Registration Deadline:*",
            "• Within 21 days: Free",
            "• 21 days - 1 year: ₹5-50",
            "• After 1 year: ₹10-100 + Magistrate order required",
            "",
            "*Documents Required:*",
            "• Hospital death certificate",
            "• Deceased's identity proof",
            "• Informant's identity proof",
            "• Address proof",
            "",
        ]

        # Online instructions
        online = how_to.get("online", {})
        lines.extend([
            "*Get Online:*",
            f"🔗 {online.get('url', 'dc.crsorgi.gov.in/crs/')}",
            "1. Select State: Bihar",
            f"2. Select District: {district or 'Your District'}",
            "3. Choose Death Certificate",
            "4. Enter registration details",
            "",
            "*Offline:*",
            "Visit Municipal Corporation / Nagar Parishad / Gram Panchayat office",
            "",
            f"📞 Helpline: {helpline.get('national', '011-23061373')}",
            f"📞 Bihar: {helpline.get('bihar_state', '0612-2506823')}",
        ])

    return "\n".join(lines)


def _format_general_info_response(lang: str) -> str:
    """Format general certificate information."""
    if lang == "hi":
        lines = [
            "📜 *जन्म/मृत्यु प्रमाण पत्र सेवाएं*",
            "",
            "*उपलब्ध सेवाएं:*",
            "👶 जन्म प्रमाण पत्र",
            "🕯️ मृत्यु प्रमाण पत्र",
            "📋 मृत जन्म प्रमाण पत्र",
            "",
            "*ऑनलाइन पोर्टल:*",
            "🔗 dc.crsorgi.gov.in/crs/",
            "",
            "*समय सीमा:*",
            "• 21 दिन के भीतर: निःशुल्क",
            "• बाद में: शुल्क + कोर्ट ऑर्डर जरूरी",
            "",
            f"📞 हेल्पलाइन: 011-23061373",
            f"📞 बिहार: 0612-2506823",
            "",
            "_'जन्म प्रमाण पत्र' या 'मृत्यु प्रमाण पत्र' भेजें अधिक जानकारी के लिए_",
        ]
    else:
        lines = [
            "📜 *Birth/Death Certificate Services*",
            "",
            "*Available Services:*",
            "👶 Birth Certificate",
            "🕯️ Death Certificate",
            "📋 Still Birth Certificate",
            "",
            "*Online Portal:*",
            "🔗 dc.crsorgi.gov.in/crs/",
            "",
            "*Deadline:*",
            "• Within 21 days: Free",
            "• After that: Fees + Court order may be required",
            "",
            f"📞 Helpline: 011-23061373",
            f"📞 Bihar: 0612-2506823",
            "",
            "_Send 'birth certificate' or 'death certificate' for more info_",
        ]

    return "\n".join(lines)


def _format_error_response(error: str, lang: str) -> str:
    """Format error response."""
    if lang == "hi":
        return "❌ प्रमाण पत्र जानकारी प्राप्त करने में समस्या हुई। कृपया बाद में प्रयास करें।\n\n📞 हेल्पलाइन: 011-23061373"
    else:
        return "❌ Error getting certificate information. Please try again later.\n\n📞 Helpline: 011-23061373"
