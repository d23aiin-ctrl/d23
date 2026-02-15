"""
WhatsApp Email Handler Node.

Handles email-related queries for WhatsApp users by looking up their linked account.
"""

import logging
from typing import Dict, Any

from common.types import BotState
from ohgrt_api.config import get_settings
from ohgrt_api.db.base import SessionLocal
from ohgrt_api.db.models import User, IntegrationCredential
from ohgrt_api.services.gmail_service import GmailService

logger = logging.getLogger(__name__)


async def handle_email(state: BotState) -> BotState:
    """
    Handle email requests for WhatsApp users.

    Looks up the user by their WhatsApp phone number and fetches emails
    if Gmail is connected. Otherwise, provides instructions to link their account.

    Args:
        state: Current bot state with phone number and email query

    Returns:
        Updated state with email response
    """
    phone = state.get("whatsapp_message", {}).get("from_number", "")
    email_query = state.get("extracted_entities", {}).get("email_query", "in:inbox")
    detected_lang = state.get("detected_language", "en")

    logger.info(f"[WhatsApp Email] Handling email request for phone: {phone}, query: {email_query}")

    settings = get_settings()
    db = SessionLocal()

    try:
        # Normalize phone number (remove any formatting)
        normalized_phone = phone.replace("+", "").replace("-", "").replace(" ", "")

        # Try to find user by phone number
        user = db.query(User).filter(User.phone_number == normalized_phone).first()

        if not user:
            # Also try with country code variations
            if not normalized_phone.startswith("91"):
                user = db.query(User).filter(User.phone_number == f"91{normalized_phone}").first()

        if not user:
            # User not linked
            logger.info(f"[WhatsApp Email] No user linked for phone: {phone}")
            return _not_linked_response(state, detected_lang)

        logger.info(f"[WhatsApp Email] Found user: {user.id}, email: {user.email}")

        # Get Gmail credential
        credential = (
            db.query(IntegrationCredential)
            .filter(
                IntegrationCredential.user_id == user.id,
                IntegrationCredential.provider == "gmail",
            )
            .first()
        )

        if not credential:
            logger.info(f"[WhatsApp Email] Gmail not connected for user: {user.id}")
            return _gmail_not_connected_response(state, detected_lang)

        # Build credential dict for GmailService
        cred_dict = {
            "access_token": credential.access_token,
            "config": credential.config or {},
        }

        # Initialize Gmail service
        gmail_service = GmailService(settings, credential=cred_dict)

        if not gmail_service.available:
            return _gmail_not_connected_response(state, detected_lang)

        # Search emails
        logger.info(f"[WhatsApp Email] Searching emails with query: {email_query}")
        emails = await gmail_service.search_emails({"raw_query": email_query})

        if not emails:
            return _no_emails_response(state, detected_lang)

        # Format response for WhatsApp
        return _format_email_response(state, emails, detected_lang)

    except Exception as e:
        logger.error(f"[WhatsApp Email] Error: {e}", exc_info=True)
        return _error_response(state, str(e), detected_lang)
    finally:
        db.close()


def _not_linked_response(state: BotState, lang: str) -> BotState:
    """Response when WhatsApp number is not linked to an account."""
    if lang == "hi":
        msg = """📧 *ईमेल एक्सेस*

आपका WhatsApp नंबर अभी किसी अकाउंट से जुड़ा नहीं है।

अपने ईमेल एक्सेस करने के लिए:
1. https://d23.ai पर जाएं
2. Google से लॉगिन करें
3. Settings में अपना WhatsApp नंबर जोड़ें
4. Gmail कनेक्ट करें

इसके बाद आप WhatsApp पर ईमेल देख सकेंगे! 📱"""
    else:
        msg = """📧 *Email Access*

Your WhatsApp number is not linked to an account yet.

To access your emails:
1. Visit https://d23.ai
2. Sign in with Google
3. Add your WhatsApp number in Settings
4. Connect Gmail

After that, you can view emails on WhatsApp! 📱"""

    state["response_text"] = msg
    state["response_type"] = "text"
    state["intent"] = "read_email"
    return state


def _gmail_not_connected_response(state: BotState, lang: str) -> BotState:
    """Response when Gmail is not connected."""
    if lang == "hi":
        msg = """📧 *Gmail कनेक्ट नहीं है*

आपका अकाउंट मिल गया, लेकिन Gmail कनेक्ट नहीं है।

Gmail कनेक्ट करने के लिए:
1. https://d23.ai/settings पर जाएं
2. Integrations में Gmail को कनेक्ट करें

इसके बाद आप WhatsApp पर ईमेल देख सकेंगे! 📱"""
    else:
        msg = """📧 *Gmail Not Connected*

Your account is linked, but Gmail is not connected.

To connect Gmail:
1. Visit https://d23.ai/settings
2. Connect Gmail in Integrations

After that, you can view emails on WhatsApp! 📱"""

    state["response_text"] = msg
    state["response_type"] = "text"
    state["intent"] = "read_email"
    return state


def _no_emails_response(state: BotState, lang: str) -> BotState:
    """Response when no emails found."""
    if lang == "hi":
        msg = "📭 कोई ईमेल नहीं मिला।"
    else:
        msg = "📭 No emails found."

    state["response_text"] = msg
    state["response_type"] = "text"
    state["intent"] = "read_email"
    return state


def _error_response(state: BotState, error: str, lang: str) -> BotState:
    """Response when an error occurs."""
    if lang == "hi":
        msg = f"❌ ईमेल लाने में समस्या हुई। कृपया बाद में प्रयास करें।"
    else:
        msg = f"❌ Error fetching emails. Please try again later."

    state["response_text"] = msg
    state["response_type"] = "text"
    state["intent"] = "read_email"
    state["error"] = error
    return state


def _format_email_response(state: BotState, emails: list, lang: str) -> BotState:
    """Format email list for WhatsApp."""
    # Build text response
    if lang == "hi":
        lines = [f"📧 *आपके {len(emails)} ईमेल:*\n"]
    else:
        lines = [f"📧 *Your {len(emails)} email(s):*\n"]

    for i, email in enumerate(emails[:5], 1):  # Show top 5
        sender = email.get("from", "Unknown")
        # Extract name from "Name <email>" format
        if "<" in sender:
            sender = sender.split("<")[0].strip().strip('"')

        subject = email.get("subject", "(No subject)")
        snippet = email.get("snippet", "")[:60]
        date = email.get("date", "")

        # Format date simply
        if date:
            try:
                from datetime import datetime
                dt = datetime.strptime(date[:25], "%a, %d %b %Y %H:%M:%S")
                date = dt.strftime("%d %b, %I:%M %p")
            except:
                date = date[:20] if len(date) > 20 else date

        lines.append(f"*{i}. {sender}*")
        lines.append(f"📌 {subject}")
        if snippet:
            lines.append(f"_{snippet}..._")
        if date:
            lines.append(f"🕐 {date}")
        lines.append("")

    if len(emails) > 5:
        remaining = len(emails) - 5
        if lang == "hi":
            lines.append(f"_...और {remaining} ईमेल_")
        else:
            lines.append(f"_...and {remaining} more email(s)_")

    lines.append("\n💡 _Visit d23.ai for full email view_")

    state["response_text"] = "\n".join(lines)
    state["response_type"] = "text"
    state["intent"] = "read_email"
    return state
