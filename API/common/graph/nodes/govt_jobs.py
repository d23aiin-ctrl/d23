"""
Government Jobs Node

Fetches state-wise or central government job openings via web search
and formats links + short summaries.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from common.graph.state import BotState
from common.tools.serper_search import search_google
from common.utils.response_formatter import sanitize_error

logger = logging.getLogger(__name__)

INTENT = "govt_jobs"

STATE_ALIASES = {
    "andhra pradesh": "Andhra Pradesh",
    "andhrapradesh": "Andhra Pradesh",
    "ap": "Andhra Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "delhi": "Delhi",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "kerla": "Kerala",
    "madhya pradesh": "Madhya Pradesh",
    "mp": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "tamil nadu": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "tn": "Tamil Nadu",
    "telangana": "Telangana",
    "uttar pradesh": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "west bengal": "West Bengal",
    "wb": "West Bengal",
    "jammu": "Jammu & Kashmir",
    "kashmir": "Jammu & Kashmir",
}


def _extract_state(query: str) -> Optional[str]:
    query_lower = query.lower()
    for key, label in STATE_ALIASES.items():
        if key in query_lower:
            return label
    match = re.search(r"(?:in|for)\s+([a-zA-Z\s]+)$", query_lower)
    if match:
        candidate = match.group(1).strip()
        return candidate.title() if candidate else None
    return None


def _build_search_query(state: Optional[str]) -> str:
    if state:
        return (
            f"government jobs {state} vacancy recruitment "
            "site:gov.in OR site:nic.in OR site:india.gov.in"
        )
    return (
        "central government jobs recruitment vacancy "
        "site:india.gov.in OR site:gov.in"
    )


def _format_items(results: List[Dict[str, str]], lang: str) -> List[str]:
    """Format job items concisely for WhatsApp."""
    lines: List[str] = []
    for idx, item in enumerate(results[:5], 1):  # Only top 5
        title = item.get("title", "").strip()
        link = item.get("link", "").strip()

        if not title:
            continue

        # Clean up title - remove common suffixes
        title = re.sub(r'\s*[-–|]\s*(FreeJobAlert|Sarkari|Result|Notification).*$', '', title, flags=re.IGNORECASE)
        title = title[:60] + "..." if len(title) > 60 else title

        lines.append(f"{idx}. *{title}*")
        if link:
            lines.append(f"   🔗 {link}")
        lines.append("")
    return lines


async def handle_govt_jobs(state: BotState) -> dict:
    user_message = state.get("current_query", "").strip() or state.get("whatsapp_message", {}).get("text", "")
    detected_lang = state.get("detected_language", "en")

    state_name = _extract_state(user_message or "")
    search_query = _build_search_query(state_name)

    try:
        result = await search_google(query=search_query, max_results=10, country="in", locale="en")
        if not result["success"]:
            error_msg = sanitize_error(result.get("error", ""), "search")
            return {
                "tool_result": result,
                "response_text": error_msg or "Could not fetch jobs right now.",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        results = (result.get("data") or {}).get("results", [])

        # Concise header
        if detected_lang == "hi":
            header = f"📋 *{state_name} सरकारी नौकरी*" if state_name else "📋 *सरकारी नौकरी अपडेट्स*"
            lines = [header, ""]
        else:
            header = f"📋 *{state_name} Govt Jobs*" if state_name else "📋 *Govt Job Updates*"
            lines = [header, ""]

        lines.extend(_format_items(results, detected_lang))

        # Short footer
        if detected_lang == "hi":
            lines.append("_और jobs के लिए \"more\" टाइप करें_")
        else:
            lines.append("_Type \"more\" for more jobs_")

        response_text = "\n".join([line for line in lines if line is not None])
        return {
            "tool_result": result,
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Govt jobs handler error: {e}")
        return {
            "response_text": "Could not fetch jobs right now.",
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
