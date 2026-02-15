"""Email handler for chat service."""

import logging
from typing import Any, Dict

from ohgrt_api.config import get_settings
from ohgrt_api.db.base import SessionLocal
from ohgrt_api.db.models import IntegrationCredential, User
from ohgrt_api.services.gmail_service import GmailService

logger = logging.getLogger(__name__)


async def handle_email(
    firebase_uid: str,
    email_query: str = "in:inbox",
    detected_language: str = "en",
) -> Dict[str, Any]:
    """
    Handle email-related queries by fetching emails from Gmail.

    Args:
        firebase_uid: The user's Firebase UID
        email_query: Gmail search query (default: inbox)
        detected_language: Detected language for response

    Returns:
        Dict with response text and structured email data
    """
    logger.info(f"[EmailHandler] Starting for user: {firebase_uid}, query: {email_query}")
    settings = get_settings()

    # Get database session
    db = SessionLocal()
    try:
        # Find user by Firebase UID
        logger.info(f"[EmailHandler] Looking up user by firebase_uid: {firebase_uid}")
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            logger.warning(f"[EmailHandler] User not found for firebase_uid: {firebase_uid}")
            return _error_response(
                "User not found. Please sign in again.",
                detected_language,
            )

        logger.info(f"[EmailHandler] User found: {user.id}, email: {user.email}")

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
            logger.warning(f"[EmailHandler] Gmail not connected for user: {user.id}")
            return _not_connected_response(detected_language)

        logger.info(f"[EmailHandler] Gmail credential found, has_token: {bool(credential.access_token)}")

        # Build credential dict for GmailService
        cred_dict = {
            "access_token": credential.access_token,
            "config": credential.config or {},
        }

        # Initialize Gmail service with user's credential
        logger.info("[EmailHandler] Initializing GmailService...")
        gmail_service = GmailService(settings, credential=cred_dict)

        if not gmail_service.available:
            logger.warning("[EmailHandler] GmailService not available after initialization")
            return _not_connected_response(detected_language)

        logger.info(f"[EmailHandler] GmailService ready, searching emails with query: {email_query}")

        # Search emails
        emails = await gmail_service.search_emails({"raw_query": email_query})

        logger.info(f"[EmailHandler] Search complete, found {len(emails) if emails else 0} emails")

        if not emails:
            return _no_emails_response(detected_language)

        # Format response
        response = _format_email_response(emails, detected_language)
        logger.info(f"[EmailHandler] Returning response with {len(emails)} emails")
        return response

    except Exception as e:
        logger.error(f"Email handler error: {e}", exc_info=True)
        return _error_response(
            f"Failed to fetch emails: {str(e)}",
            detected_language,
        )
    finally:
        db.close()


def _not_connected_response(lang: str) -> Dict[str, Any]:
    """Return response when Gmail is not connected."""
    if lang == "hi":
        msg = "Gmail कनेक्ट नहीं है। कृपया Settings > Integrations में जाकर Gmail कनेक्ट करें।"
    else:
        msg = "Gmail is not connected. Please connect Gmail via Settings > Integrations."

    return {
        "response_text": msg,
        "response_type": "text",
        "intent": "read_email",
        "structured_data": {"type": "gmail_not_connected"},
    }


def _no_emails_response(lang: str) -> Dict[str, Any]:
    """Return response when no emails found."""
    if lang == "hi":
        msg = "कोई ईमेल नहीं मिला।"
    else:
        msg = "No emails found."

    return {
        "response_text": msg,
        "response_type": "text",
        "intent": "read_email",
        "structured_data": {"type": "no_emails"},
    }


def _error_response(error: str, lang: str) -> Dict[str, Any]:
    """Return error response."""
    if lang == "hi":
        msg = f"ईमेल लाने में समस्या: {error}"
    else:
        msg = f"Error fetching emails: {error}"

    return {
        "response_text": msg,
        "response_type": "text",
        "intent": "read_email",
        "error": error,
    }


def _format_email_response(
    emails: list,
    lang: str,
) -> Dict[str, Any]:
    """Format email list as response."""
    # Build text response
    if lang == "hi":
        response_lines = [f"आपके {len(emails)} ईमेल:\n"]
    else:
        response_lines = [f"Found {len(emails)} email(s):\n"]

    for i, email in enumerate(emails[:5], 1):  # Show top 5
        sender = email.get("from", "Unknown")
        # Extract name from "Name <email>" format
        if "<" in sender:
            sender = sender.split("<")[0].strip().strip('"')
        subject = email.get("subject", "(No subject)")
        snippet = email.get("snippet", "")[:80]

        response_lines.append(f"{i}. **{sender}**")
        response_lines.append(f"   {subject}")
        if snippet:
            response_lines.append(f"   _{snippet}..._")
        response_lines.append("")

    response_text = "\n".join(response_lines)

    # Build structured data for frontend
    email_list = []
    for email in emails:
        email_list.append({
            "id": email.get("id"),
            "from": email.get("from", ""),
            "subject": email.get("subject", ""),
            "snippet": email.get("snippet", ""),
            "date": email.get("date", ""),
        })

    return {
        "response_text": response_text,
        "response_type": "text",
        "intent": "read_email",
        "structured_data": {
            "type": "email_list",
            "emails": email_list,
            "count": len(emails),
        },
    }
