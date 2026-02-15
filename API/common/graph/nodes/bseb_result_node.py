"""
BSEB Result Information Node

Handles queries about Bihar School Examination Board matric results.
"""

import logging
import re
from typing import Optional, Dict

from common.graph.state import BotState
from common.tools.bseb_result_tool import (
    handle_bseb_result_query,
    get_result_check_info,
    get_result_format_info,
    extract_roll_code_and_number
)
from common.services.ai_language_service import ai_translate_response
from common.config.settings import settings

logger = logging.getLogger(__name__)


def extract_roll_number(text: str) -> Optional[str]:
    """
    Extract roll number from user message.

    Args:
        text: User message

    Returns:
        Roll number or None
    """
    # Common patterns for roll numbers
    patterns = [
        r'roll\s*(?:number|no|num)?\s*(?:is|:)?\s*(\d{4,10})',
        r'my\s*roll\s*(?:number|no)?\s*(?:is)?\s*(\d{4,10})',
        r'(\d{6,10})',  # Just a sequence of digits
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)

    return None


async def bseb_result_node(state: BotState) -> dict:
    """
    Handle BSEB result information queries.

    Args:
        state: Current bot state

    Returns:
        Response with BSEB result information
    """
    user_message = state.get("current_query", "") or state.get("user_message", "")
    detected_language = state.get("detected_language", "en")

    logger.info(f"Processing BSEB result query: {user_message[:100]}...")

    try:
        # Extract roll code and number if mentioned
        extracted = extract_roll_code_and_number(user_message)
        roll_code = extracted.get("roll_code")
        roll_number = extracted.get("roll_number")

        logger.info(f"Extracted - Roll Code: {roll_code}, Roll Number: {roll_number}")

        # Handle the query (async)
        result = await handle_bseb_result_query(
            query=user_message,
            roll_number=roll_number,
            roll_code=roll_code,
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
                "intent": "bseb_result",
                "should_fallback": False,
            }
        else:
            # Fallback to general information
            response = get_result_check_info()

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
                "intent": "bseb_result",
                "should_fallback": False,
            }

    except Exception as e:
        logger.error(f"Error in BSEB result node: {e}", exc_info=True)

        error_message = "I encountered an error while fetching BSEB result information. Here's general information about checking your Bihar Board matric result:"
        general_info = get_result_check_info()

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
            "intent": "bseb_result",
            "should_fallback": False,
        }
