"""
Train Running Status Node

Checks live train running status using web scraping for detailed information.
"""

import logging
from datetime import datetime
from common.graph.state import BotState
from common.tools.train_scraper import scrape_train_status_detailed
from common.utils.response_formatter import sanitize_error, create_service_error_response
from common.utils.entity_extraction import extract_train_number
from common.i18n.detector import detect_language

logger = logging.getLogger(__name__)

# Intent constant
INTENT = "train_status"


def _format_train_status_hindi(data: dict, train_number: str) -> str:
    """Format train status in Hindi style matching the expected output."""
    lines = []

    # Header
    train_name = data.get("train_name", "Unknown Train")
    lines.append(f"🚂 *ट्रेन स्टेटस: {train_name} ({train_number})*")

    # Route
    source = data.get("source", "")
    destination = data.get("destination", "")
    if source and destination:
        lines.append(f"*मार्ग:* {source} से {destination}")

    # Travel date
    travel_date = data.get("travel_date", "")
    if travel_date:
        # Convert to Hindi date format
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

    # Current Status Section
    current_station = data.get("current_station", "N/A")
    current_code = data.get("current_station_code", "")
    current_platform = data.get("current_platform", "अज्ञात")

    lines.append(f"🚀 *वर्तमान स्थिति (अपडेट समय: {data.get('fetched_at', 'N/A').split()[1]}):*")
    lines.append("")

    # Station
    if current_code:
        lines.append(f"• *स्टेशन:* {current_station} ({current_code})")
    else:
        lines.append(f"• *स्टेशन:* {current_station}")

    # ETA/ETD
    current_arrival = data.get("current_arrival", "")
    current_departure = data.get("current_departure", "")
    if current_arrival:
        lines.append(f"• *पहुंच समय (ETA):* {current_arrival}")
    if current_departure:
        lines.append(f"• *प्रस्थान समय (ETD):* {current_departure}")

    # Platform
    if current_platform and current_platform != "अज्ञात":
        lines.append(f"• *प्लेटफॉर्म:* {current_platform}")

    # Status/Delay
    running_status = data.get("running_status", "Unknown")
    lines.append(f"• *स्थिति:* {running_status}")

    lines.append("")

    # Journey Progress
    distance_traveled = data.get("distance_traveled", 0)
    total_distance = data.get("total_distance", 0)
    if distance_traveled > 0 or total_distance > 0:
        lines.append(f"📍 *यात्रा प्रगति:*")
        if total_distance > 0:
            lines.append(f"*{distance_traveled} किमी (कुल {total_distance} किमी में से)*")
        else:
            lines.append(f"*{distance_traveled} किमी*")
        lines.append("")

    # Next Major Stops
    next_stations = data.get("next_stations", [])
    if next_stations:
        lines.append(f"⏩ *अगले प्रमुख स्टॉप:*")
        lines.append("")
        for station in next_stations[:6]:
            station_name = station.get("name", "")
            station_code = station.get("code", "")
            arrival = station.get("arrival", "")
            departure = station.get("departure", "")
            platform = station.get("platform", "")

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

    # Footer
    data_source = data.get("data_source", "")
    fetched_at = data.get("fetched_at", "")
    lines.append(f"*Data Fetched at the time: {fetched_at}*")

    return "\n".join(lines)


def _format_train_status_english(data: dict, train_number: str) -> str:
    """Format train status in English."""
    lines = []

    # Header
    train_name = data.get("train_name", "Unknown Train")
    lines.append(f"🚂 *{train_name} ({train_number})*")

    # Route
    source = data.get("source", "")
    destination = data.get("destination", "")
    if source and destination:
        lines.append(f"*Route:* {source} to {destination}")

    # Travel date
    travel_date = data.get("travel_date", "")
    if travel_date:
        lines.append(f"*Travel Date:* {travel_date}")

    # Last update
    last_update = data.get("last_update", "")
    if last_update:
        lines.append(f"*Last Update:* {last_update}")

    lines.append("")

    # Current Status
    current_station = data.get("current_station", "N/A")
    current_code = data.get("current_station_code", "")
    current_platform = data.get("current_platform", "Unknown")
    current_arrival = data.get("current_arrival", "")
    current_departure = data.get("current_departure", "")
    running_status = data.get("running_status", "Unknown")

    lines.append(f"📍 *Current:* {current_station}" + (f" ({current_code})" if current_code else ""))
    if current_platform and current_platform != "Unknown":
        lines.append(f"*Platform:* {current_platform}")
    if current_arrival:
        lines.append(f"*Arrival:* {current_arrival}")
    if current_departure:
        lines.append(f"*Departure:* {current_departure}")
    lines.append(f"⏱️ *Status:* {running_status}")

    lines.append("")

    # Next Stations
    next_stations = data.get("next_stations", [])
    if next_stations:
        lines.append("*Next Stations:*")
        lines.append("")
        for station in next_stations[:3]:
            station_name = station.get("name", "")
            arrival = station.get("arrival", "")
            departure = station.get("departure", "")
            timing = f"Arrival: {arrival}" if arrival else ""
            if departure and departure != arrival:
                timing += f", Departure: {departure}"
            lines.append(f"*{station_name}*")
            if timing:
                lines.append(f"{timing}")
            lines.append("")

    # Footer
    fetched_at = data.get("fetched_at", "")
    lines.append(f"*Data fetched at: {fetched_at}*")

    return "\n".join(lines)


async def handle_train_status(state: BotState) -> dict:
    """
    Node function: Check live train running status with detailed information.

    Args:
        state: Current bot state with train number in entities

    Returns:
        Updated state with detailed train status or error
    """
    entities = state.get("extracted_entities", {})
    train_number = entities.get("train_number", "")
    query = state.get("current_query", "") or state.get("whatsapp_message", {}).get("text", "")

    # Try to extract train number from query if not in entities
    if not train_number:
        train_number = extract_train_number(query) or ""

    # Validate train number
    if not train_number:
        return {
            "response_text": (
                "*Train Status*\n\n"
                "Please provide a train number.\n\n"
                "*Example:* Live train status 12301\n\n"
                "*Popular trains:*\n"
                "- 12301/12302 - Rajdhani Express\n"
                "- 12951/12952 - Mumbai Rajdhani\n"
                "- 22691/22692 - Rajdhani Express"
            ),
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    try:
        # Use detailed scraper
        result = await scrape_train_status_detailed(train_number)

        if result["success"]:
            data = result["data"]

            # Detect language from query
            detected_lang = detect_language(query)

            # Format based on language preference
            if detected_lang == "hi":
                response_text = _format_train_status_hindi(data, train_number)
            else:
                response_text = _format_train_status_english(data, train_number)

            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }
        else:
            error_msg = result.get("error", "Unable to fetch train status")
            return {
                "tool_result": result,
                "response_text": (
                    f"*Train Status: {train_number}*\n\n"
                    f"❌ {error_msg}\n\n"
                    "*Possible reasons:*\n"
                    "- Train not running today\n"
                    "- Invalid train number\n"
                    "- Website temporarily unavailable\n\n"
                    "_Please verify and try again._"
                ),
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

    except Exception as e:
        logger.error(f"Train status handler error: {e}", exc_info=True)
        return create_service_error_response(
            intent=INTENT,
            feature_name="Train Status",
            raw_error=str(e)
        )
