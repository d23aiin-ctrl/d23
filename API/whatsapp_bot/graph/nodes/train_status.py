"""
Train Status Node.

Handles train running status queries with detailed information.
Uses railway_api module with fallback to web scraping when API fails.
Supports multi-language responses with emoji-rich formatting.
"""

import logging
import re
from typing import Dict, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from common.graph.state import BotState
from common.tools.railway_api import get_train_status_async
from common.tools.train_scraper import scrape_train_status, scrape_train_status_detailed
from whatsapp_bot.config import settings

logger = logging.getLogger(__name__)

INTENT = "train_status"

# Language names for prompts
LANGUAGE_NAMES = {
    "en": {"en": "English", "native": "English"},
    "hi": {"en": "Hindi", "native": "हिंदी"},
    "kn": {"en": "Kannada", "native": "ಕನ್ನಡ"},
    "ta": {"en": "Tamil", "native": "தமிழ்"},
    "te": {"en": "Telugu", "native": "తెలుగు"},
    "bn": {"en": "Bengali", "native": "বাংলা"},
    "mr": {"en": "Marathi", "native": "मराठी"},
    "or": {"en": "Odia", "native": "ଓଡ଼ିଆ"},
    "gu": {"en": "Gujarati", "native": "ગુજરાતી"},
    "pa": {"en": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "ml": {"en": "Malayalam", "native": "മലയാളം"},
}

# Hindi labels for the detailed format
HINDI_LABELS = {
    "train_details": "ट्रेन के विवरण हिंदी में:",
    "train": "🚆",
    "route": "📍 शुरुआत:",
    "travel_date": "🗓️ यात्रा तिथि:",
    "scheduled_departure": "⏱️ निर्धारित रवानगी:",
    "last_update": "🔄 अंतिम अपडेट:",
    "current": "📊 वर्तमान:",
    "platform": "प्लेटफॉर्म",
    "platform_unknown": "अज्ञात",
    "arrival_time": "आगमन समय:",
    "departure_time": "प्रस्थान समय:",
    "status": "⏰ स्थिति:",
    "delay_suffix": "(कुछ सेकंड पहले)",
    "distance": "📏 दूरी:",
    "distance_format": "मूल से {traveled}/{total} किमी",
    "next_stations": "अगले स्टेशन:",
    "fetched_at": "डेटा प्राप्त किया गया समय:",
    "from_to": "से",
    "for": "के लिए",
    "on_time": "समय पर",
    "minutes_late": "मिनट की देरी",
    "minutes_early": "मिनट पहले",
}

# English labels
ENGLISH_LABELS = {
    "train_details": "Train Details:",
    "train": "🚆",
    "route": "📍 Route:",
    "travel_date": "🗓️ Travel Date:",
    "scheduled_departure": "⏱️ Scheduled Departure:",
    "last_update": "🔄 Last Update:",
    "current": "📊 Current:",
    "platform": "Platform",
    "platform_unknown": "Unknown",
    "arrival_time": "Arrival:",
    "departure_time": "Departure:",
    "status": "⏰ Status:",
    "delay_suffix": "(just now)",
    "distance": "📏 Distance:",
    "distance_format": "{traveled}/{total} km from origin",
    "next_stations": "Next Stations:",
    "fetched_at": "Data fetched at:",
    "from_to": "to",
    "for": "for",
    "on_time": "On Time",
    "minutes_late": "minutes late",
    "minutes_early": "minutes early",
}


def extract_train_number(text: str) -> Optional[str]:
    """
    Extract train number from text.

    Args:
        text: User message

    Returns:
        Train number or None
    """
    # Train numbers are typically 5 digits
    match = re.search(r'\b(\d{5})\b', text)
    if match:
        return match.group(1)
    return None


def format_detailed_train_status(data: Dict, lang: str = "hi") -> str:
    """
    Format train status data in detailed emoji format matching the expected output.

    Args:
        data: Train status data from scraper
        lang: Language code (hi for Hindi, en for English)

    Returns:
        Formatted message with emojis
    """
    if not data:
        return "Could not fetch train status. Please check the train number."

    train_name = data.get("train_name", "Unknown")
    train_number = data.get("train_number", "")
    source = data.get("source", "")
    destination = data.get("destination", "")
    travel_date = data.get("travel_date", datetime.now().strftime("%Y-%m-%d"))
    current_station = data.get("current_station", "N/A")
    current_code = data.get("current_station_code", "")
    current_platform = data.get("current_platform", "अज्ञात" if lang == "hi" else "Unknown")
    current_arrival = data.get("current_arrival", "")
    current_departure = data.get("current_departure", "")
    running_status = data.get("running_status", "Unknown")
    distance_traveled = data.get("distance_traveled", 0)
    total_distance = data.get("total_distance", 0)
    next_stations = data.get("next_stations", [])
    fetched_at = data.get("fetched_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"))

    lines = []

    if lang == "hi":
        # Header
        lines.append(f"🚂 *ट्रेन स्टेटस: {train_name} ({train_number})*")

        # Route
        if source and destination:
            lines.append(f"*मार्ग:* {source} से {destination}")

        # Travel date
        if travel_date:
            try:
                dt = datetime.strptime(travel_date, "%Y-%m-%d")
                hindi_date = dt.strftime("%d %B %Y")
                # Convert month names to Hindi
                month_map = {
                    "January": "जनवरी", "February": "फरवरी", "March": "मार्च",
                    "April": "अप्रैल", "May": "मई", "June": "जून",
                    "July": "जुलाई", "August": "अगस्त", "September": "सितंबर",
                    "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
                }
                for eng, hin in month_map.items():
                    hindi_date = hindi_date.replace(eng, hin)
                lines.append(f"*यात्रा तिथि:* {hindi_date}")
            except:
                lines.append(f"*यात्रा तिथि:* {travel_date}")

        lines.append("")

        # Current Status Section - extract time from fetched_at
        try:
            update_time = fetched_at.split()[1] if ' ' in fetched_at else fetched_at
        except:
            update_time = "N/A"

        lines.append(f"🚀 *वर्तमान स्थिति (अपडेट समय: {update_time}):*")
        lines.append("")

        # Station
        if current_code:
            lines.append(f"• *स्टेशन:* {current_station} ({current_code})")
        else:
            lines.append(f"• *स्टेशन:* {current_station}")

        # ETA/ETD
        if current_arrival:
            lines.append(f"• *पहुंच समय (ETA):* {current_arrival}")
        if current_departure:
            lines.append(f"• *प्रस्थान समय (ETD):* {current_departure}")

        # Platform
        if current_platform and current_platform != "अज्ञात":
            lines.append(f"• *प्लेटफॉर्म:* {current_platform}")

        # Status/Delay
        lines.append(f"• *स्थिति:* {running_status}")

        lines.append("")

        # Journey Progress
        if distance_traveled > 0 or total_distance > 0:
            lines.append(f"📍 *यात्रा प्रगति:*")
            if total_distance > 0:
                lines.append(f"*{distance_traveled} किमी (कुल {total_distance} किमी में से)*")
            else:
                lines.append(f"*{distance_traveled} किमी*")
            lines.append("")

        # Next Major Stops
        if next_stations:
            lines.append(f"⏩ *अगले प्रमुख स्टॉप:*")
            lines.append("")
            for station in next_stations[:6]:
                station_name = station.get("name", "")
                station_code = station.get("code", "")
                arrival = station.get("arrival", "")
                departure = station.get("departure", "")

                if not station_name:
                    continue

                # Station name with code
                if station_code:
                    station_label = f"• *{station_name} ({station_code}):*"
                else:
                    station_label = f"• *{station_name}:*"

                # Timing info
                timing_parts = []
                if arrival:
                    timing_parts.append(f"{arrival} पर पहुंच")
                if departure:
                    timing_parts.append(f"{departure} पर प्रस्थान")

                if timing_parts:
                    lines.append(f"{station_label} {', '.join(timing_parts)}")
                else:
                    lines.append(station_label)

        lines.append("")
        lines.append(f"*Data Fetched at the time: {fetched_at}*")

    else:  # English
        # Header
        lines.append(f"🚂 *Train Status: {train_name} ({train_number})*")

        # Route
        if source and destination:
            lines.append(f"*Route:* {source} to {destination}")

        # Travel date
        if travel_date:
            lines.append(f"*Travel Date:* {travel_date}")

        lines.append("")

        # Current Status Section
        try:
            update_time = fetched_at.split()[1] if ' ' in fetched_at else fetched_at
        except:
            update_time = "N/A"

        lines.append(f"🚀 *Current Status (Update time: {update_time}):*")
        lines.append("")

        # Station
        if current_code:
            lines.append(f"• *Station:* {current_station} ({current_code})")
        else:
            lines.append(f"• *Station:* {current_station}")

        # ETA/ETD
        if current_arrival:
            lines.append(f"• *Arrival Time (ETA):* {current_arrival}")
        if current_departure:
            lines.append(f"• *Departure Time (ETD):* {current_departure}")

        # Platform
        if current_platform and current_platform != "Unknown":
            lines.append(f"• *Platform:* {current_platform}")

        # Status
        lines.append(f"• *Status:* {running_status}")

        lines.append("")

        # Journey Progress
        if distance_traveled > 0 or total_distance > 0:
            lines.append(f"📍 *Journey Progress:*")
            if total_distance > 0:
                lines.append(f"*{distance_traveled} km (out of {total_distance} km total)*")
            else:
                lines.append(f"*{distance_traveled} km*")
            lines.append("")

        # Next Major Stops
        if next_stations:
            lines.append(f"⏩ *Next Major Stops:*")
            lines.append("")
            for station in next_stations[:6]:
                station_name = station.get("name", "")
                station_code = station.get("code", "")
                arrival = station.get("arrival", "")
                departure = station.get("departure", "")

                if not station_name:
                    continue

                # Station name with code
                if station_code:
                    station_label = f"• *{station_name} ({station_code}):*"
                else:
                    station_label = f"• *{station_name}:*"

                # Timing info
                timing_parts = []
                if arrival:
                    timing_parts.append(f"arrives {arrival}")
                if departure:
                    timing_parts.append(f"departs {departure}")

                if timing_parts:
                    lines.append(f"{station_label} {', '.join(timing_parts)}")
                else:
                    lines.append(station_label)

        lines.append("")
        lines.append(f"*Data Fetched at the time: {fetched_at}*")

    return "\n".join(lines)


def format_train_status_simple(data: Dict) -> str:
    """
    Format train status data as a simple readable message (fallback).

    Args:
        data: Train status data

    Returns:
        Formatted message
    """
    if not data:
        return "Could not fetch train status. Please check the train number."

    train_name = data.get("train_name", "Unknown")
    train_number = data.get("train_number", "")
    running_status = data.get("running_status", "")
    delay = data.get("delay_minutes", 0)
    last_station = data.get("last_station", data.get("current_station", "N/A"))
    last_time = data.get("last_station_time", "")
    next_station = data.get("next_station", "N/A")
    eta = data.get("eta_next_station", "")
    source = data.get("source", "")
    destination = data.get("destination", "")

    # Format delay message
    if delay == 0:
        delay_msg = "On time"
    elif delay > 0:
        delay_msg = f"{delay} mins late"
    else:
        delay_msg = f"{abs(delay)} mins early"

    lines = [
        f"*Train Status: {train_name} ({train_number})*",
        "",
    ]

    if source and destination:
        lines.append(f"Route: {source} -> {destination}")

    lines.extend([
        f"Status: {running_status}",
        f"Delay: {delay_msg}",
        "",
        f"Last Station: {last_station}",
    ])

    if last_time:
        lines.append(f"Time: {last_time}")

    if next_station and next_station != "N/A":
        lines.append(f"Next Station: {next_station}")
        if eta:
            lines.append(f"ETA: {eta}")

    return "\n".join(lines)


async def translate_response(text: str, lang_code: str) -> str:
    """
    Translate response text to the specified language using LLM.

    Args:
        text: Text to translate
        lang_code: Target language code (e.g., 'kn' for Kannada)

    Returns:
        Translated text, or original if translation fails
    """
    # Skip if already Hindi (our default format) or English
    if lang_code in ["en", "hi"] or lang_code not in LANGUAGE_NAMES:
        return text

    try:
        lang_info = LANGUAGE_NAMES.get(lang_code, {})
        language_name = lang_info.get("en", "English")

        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a translator. Translate the following train status information to {language_name} ({language_code}).

Keep the formatting with emojis intact.
Use the appropriate script for the language (e.g., Kannada script for Kannada, Tamil script for Tamil).
Keep train numbers, times, station codes, and dates in English/numerals.
Make the translation natural and fluent.

IMPORTANT: Only output the translated text, nothing else."""),
            ("human", "{text}")
        ])

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=settings.openai_api_key,
        )

        chain = translate_prompt | llm
        result = chain.invoke({
            "text": text,
            "language_name": language_name,
            "language_code": lang_code,
        })

        return result.content.strip()
    except Exception as e:
        logger.warning(f"Translation failed for {lang_code}: {e}")
        return text  # Return original if translation fails


def detect_requested_language(query: str, detected_lang: str) -> str:
    """
    Detect if user explicitly requested a specific language.

    Args:
        query: User's query
        detected_lang: Auto-detected language

    Returns:
        Language code
    """
    query_lower = query.lower()

    # Check for explicit language requests
    language_keywords = {
        "hi": ["hindi", "हिंदी", "हिन्दी"],
        "kn": ["kannada", "ಕನ್ನಡ"],
        "ta": ["tamil", "தமிழ்"],
        "te": ["telugu", "తెలుగు"],
        "bn": ["bengali", "বাংলা", "bangla"],
        "mr": ["marathi", "मराठी"],
        "or": ["odia", "ଓଡ଼ିଆ", "oriya"],
        "gu": ["gujarati", "ગુજરાતી"],
        "pa": ["punjabi", "ਪੰਜਾਬੀ"],
        "ml": ["malayalam", "മലയാളം"],
        "en": ["english", "in english"],
    }

    for lang_code, keywords in language_keywords.items():
        for kw in keywords:
            if kw in query_lower or kw in query:
                return lang_code

    return detected_lang


async def handle_train_status(state: BotState) -> Dict:
    """
    Handle train status queries with detailed emoji format.

    Uses railway_api module with fallback to web scraping when API fails.

    Args:
        state: Current bot state

    Returns:
        State update with train status
    """
    query = state.get("current_query", "")
    entities = state.get("extracted_entities", {})
    detected_lang = state.get("detected_language", "en")

    # Check for explicit language request
    target_lang = detect_requested_language(query, detected_lang)

    # Extract train number
    train_number = entities.get("train_number") or extract_train_number(query)

    if not train_number:
        # Response in Hindi if detected language is Hindi
        if target_lang == "hi":
            return {
                "response_text": (
                    "कृपया ट्रेन नंबर प्रदान करें।\n"
                    "उदाहरण: ट्रेन 12301 की स्थिति"
                ),
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
                "route_log": state.get("route_log", []) + ["train_status:missing_number"],
            }
        return {
            "response_text": (
                "Please provide the train number.\n"
                "Example: Train status 12301"
            ),
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
            "route_log": state.get("route_log", []) + ["train_status:missing_number"],
        }

    data = None
    error_msg = None

    # Try RapidAPI first
    try:
        result = await get_train_status_async(train_number)
        if result["success"] and result.get("data"):
            data = result["data"]
            logger.info(f"Train status fetched via RapidAPI for {train_number}")
        else:
            error_msg = result.get("error", "API error")
            logger.warning(f"RapidAPI failed for {train_number}: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"RapidAPI exception for {train_number}: {e}")

    # Fallback to detailed web scraping if API failed
    if not data:
        try:
            logger.info(f"Falling back to detailed web scraper for {train_number}")
            scrape_result = await scrape_train_status_detailed(train_number)
            if scrape_result["success"] and scrape_result.get("data"):
                data = scrape_result["data"]
                logger.info(f"Train status fetched via detailed scraper for {train_number}")
            else:
                error_msg = scrape_result.get("error", "Scraping failed")
                logger.warning(f"Detailed scraper failed for {train_number}: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Detailed scraper exception for {train_number}: {e}")

    # Return response
    if data:
        # Default to Hindi format for Indian trains (better UX for Indian users)
        # Only use English if explicitly requested with "in english" or "english"
        query_lower = query.lower()
        force_english = any(kw in query_lower for kw in ["in english", "english mein", "english me"])

        if force_english:
            response = format_detailed_train_status(data, "en")
        elif target_lang == "hi" or target_lang == "en":
            # Default to Hindi for Indian context
            response = format_detailed_train_status(data, "hi")
        else:
            # Format in Hindi first, then translate to other languages
            response = format_detailed_train_status(data, "hi")

        # Translate if not Hindi or English
        if target_lang not in ["hi", "en"] and not force_english:
            logger.info(f"Translating train status to {target_lang}")
            response = await translate_response(response, target_lang)

        return {
            "response_text": response,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
            "tool_result": data,
            "route_log": state.get("route_log", []) + ["train_status:success"],
        }
    else:
        # Error response in appropriate language
        if target_lang == "hi":
            return {
                "response_text": (
                    f"ट्रेन {train_number} की स्थिति प्राप्त नहीं हो सकी।\n\n"
                    "*संभावित कारण:*\n"
                    "- आज ट्रेन नहीं चल रही\n"
                    "- गलत ट्रेन नंबर\n"
                    "- सेवा अस्थायी रूप से अनुपलब्ध\n\n"
                    "_कृपया बाद में पुनः प्रयास करें।_"
                ),
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
                "error": error_msg,
                "route_log": state.get("route_log", []) + ["train_status:all_failed"],
            }
        return {
            "response_text": (
                f"Could not fetch train status for {train_number}.\n\n"
                "*Possible reasons:*\n"
                "- Train not running today\n"
                "- Invalid train number\n"
                "- Service temporarily unavailable\n\n"
                "_Please try again later._"
            ),
            "response_type": "text",
            "should_fallback": False,  # Don't fallback to chat, show this message
            "intent": INTENT,
            "error": error_msg,
            "route_log": state.get("route_log", []) + ["train_status:all_failed"],
        }
