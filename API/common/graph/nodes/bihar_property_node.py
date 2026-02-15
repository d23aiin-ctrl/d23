"""
Bihar Property Registration Node

Handles queries about property registration, stamp duty, and charges in Bihar.
"""

import logging
import re
from typing import Optional

from common.graph.state import BotState
from common.tools.bihar_property_tool import (
    handle_property_query_sync,
    calculate_charges,
    get_general_info
)
from common.services.ai_language_service import ai_translate_response
from common.config.settings import settings

logger = logging.getLogger(__name__)


def extract_property_value(text: str) -> Optional[float]:
    """
    Extract property value from user message.

    Args:
        text: User message

    Returns:
        Property value in rupees or None
    """
    # Common patterns for property value
    patterns = [
        r'(?:rs\.?|₹|rupees?)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|lakhs)?',
        r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|lakhs)',
        r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr)',
        r'(\d+(?:,\d+)*(?:\.\d+)?)',  # Just numbers
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            value_str = match.group(1).replace(',', '')
            value = float(value_str)

            # Check if it's in lakhs or crores
            if 'lakh' in text.lower() or 'lac' in text.lower():
                value = value * 100000
            elif 'crore' in text.lower() or 'cr' in text.lower():
                value = value * 10000000

            return value

    return None


def extract_gender_info(text: str) -> dict:
    """
    Extract buyer and seller gender from text.

    Args:
        text: User message

    Returns:
        Dict with buyer_gender and seller_gender
    """
    text_lower = text.lower()

    buyer_gender = None
    seller_gender = None

    # Detect buyer gender
    if any(word in text_lower for word in ['female buyer', 'woman buyer', 'lady', 'wife', 'daughter', 'mother', 'female', 'woman']):
        buyer_gender = "female"
    elif any(word in text_lower for word in ['male buyer', 'man', 'husband', 'son', 'father', 'male']):
        buyer_gender = "male"

    # Detect seller gender
    if any(word in text_lower for word in ['female seller', 'woman seller', 'from woman', 'from female']):
        seller_gender = "female"
    elif any(word in text_lower for word in ['male seller', 'man seller', 'from man', 'from male']):
        seller_gender = "male"

    return {
        "buyer_gender": buyer_gender,
        "seller_gender": seller_gender
    }


async def bihar_property_node(state: BotState) -> BotState:
    """
    Handle Bihar property registration queries.

    Args:
        state: Current bot state

    Returns:
        Updated bot state with property information
    """
    user_message = state.get("user_message", "")
    detected_language = state.get("detected_language", "en")

    logger.info(f"Processing Bihar property query: {user_message[:100]}...")

    try:
        # Extract property value if mentioned
        property_value = extract_property_value(user_message)

        # Extract gender information
        gender_info = extract_gender_info(user_message)

        # Handle the query
        result = handle_property_query_sync(
            query=user_message,
            property_value=property_value,
            buyer_gender=gender_info.get("buyer_gender"),
            seller_gender=gender_info.get("seller_gender"),
            language=detected_language
        )

        if result["success"]:
            response = result.get("data", {}).get("output", "")

            # Translate if not in English
            if detected_language != "en" and settings.OPENAI_API_KEY:
                try:
                    response = await ai_translate_response(
                        text=response,
                        target_language=detected_language,
                        openai_api_key=settings.OPENAI_API_KEY
                    )
                except Exception as e:
                    logger.warning(f"Translation failed, using English: {e}")

            return {
                "response_text": response,
                "response_type": "text",
                "intent": "bihar_property",
                "should_fallback": False,
            }
        else:
            # Fallback to general information - try to get from result data first
            response = result.get("data", {}).get("output") or get_general_info()

            if detected_language != "en" and settings.OPENAI_API_KEY:
                try:
                    response = await ai_translate_response(
                        text=response,
                        target_language=detected_language,
                        openai_api_key=settings.OPENAI_API_KEY
                    )
                except Exception as e:
                    logger.warning(f"Translation failed, using English: {e}")

            return {
                "response_text": response,
                "response_type": "text",
                "intent": "bihar_property",
                "should_fallback": False,
            }

    except Exception as e:
        logger.error(f"Error in Bihar property node: {e}", exc_info=True)

        error_message = "I encountered an error while fetching property registration information. Here's general information about Bihar property registration:"
        general_info = get_general_info()

        if detected_language != "en" and settings.OPENAI_API_KEY:
            try:
                error_message = await ai_translate_response(
                    text=error_message,
                    target_language=detected_language,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                general_info = await ai_translate_response(
                    text=general_info,
                    target_language=detected_language,
                    openai_api_key=settings.OPENAI_API_KEY
                )
            except Exception as trans_error:
                logger.warning(f"Translation failed, using English: {trans_error}")

        return {
            "response_text": f"{error_message}\n\n{general_info}",
            "response_type": "text",
            "intent": "bihar_property",
            "should_fallback": False,
        }
