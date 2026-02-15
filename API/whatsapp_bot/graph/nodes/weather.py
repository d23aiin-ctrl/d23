"""
Weather Node

Fetches and displays weather information for a given city or location.
Supports location-based weather when user shares their GPS location.
Supports multilingual responses (11+ Indian languages).

UPDATED: Now uses AI for response translation when needed.
"""

import logging
import re
from whatsapp_bot.state import BotState
from whatsapp_bot.config import settings
from common.tools.weather_api import get_weather, get_weather_by_coordinates
from common.tools.serper_search import search_google
from common.utils.response_formatter import sanitize_error, create_service_error_response
from whatsapp_bot.stores.pending_location_store import get_pending_location_store
from bot.whatsapp.client import get_whatsapp_client
from common.i18n.responses import get_weather_label, get_phrase

# AI Translation Service
try:
    from common.services.ai_language_service import ai_translate_response
    AI_TRANSLATE_AVAILABLE = True
except ImportError:
    AI_TRANSLATE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Intent constant
INTENT = "weather"

# Response type for location request
RESPONSE_TYPE_LOCATION_REQUEST = "location_request"


def _extract_city_from_query(query: str) -> str:
    """
    Extract city name from weather query.

    Examples:
    - "weather in Delhi" -> "Delhi"
    - "tell me weather of Mumbai" -> "Mumbai"
    - "what's the temperature in New York" -> "New York"
    """
    query_lower = query.lower()

    # Common patterns for city extraction
    patterns = [
        r"weather\s+(?:in|of|for|at)\s+(.+?)(?:\?|$)",
        r"(?:in|of|for|at)\s+(.+?)\s+weather",
        r"temperature\s+(?:in|of|for|at)\s+(.+?)(?:\?|$)",
        r"(?:in|of|for|at)\s+(.+?)\s+temperature",
        r"weather\s+(.+?)(?:\?|$)",
        r"(.+?)\s+weather",
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            city = match.group(1).strip()
            # Clean up common filler words
            city = re.sub(r"^(the|a|an)\s+", "", city)
            city = re.sub(r"\s+(today|tomorrow|now|please).*$", "", city)
            city = re.sub(r"\b(ka|ki|ke|का|की|के)\b$", "", city).strip()
            # Remove "near me", "here" etc as they're not city names
            if city.lower() in ["me", "here", "my location", "today", "tomorrow", "now",
                                "near me", "nearby", "around me", "for my location", "at my location"]:
                return ""
            if city and len(city) > 1:
                return city.title()

    # Fallback: look for capitalized words that might be city names
    words = query.split()
    for word in words:
        if len(word) > 1 and word[0].isupper() and word.lower() not in [
            "weather", "temperature", "what", "tell", "me", "the", "in", "of",
            "today", "tomorrow", "how", "is", "whats", "what's", "near", "here",
            "nearby", "around", "my", "location", "for", "at"
        ]:
            return word

    return ""


def _normalize_city_name(city: str) -> str:
    """Normalize city names and strip trailing Hindi postpositions."""
    if not city:
        return ""
    city_clean = city.strip()
    city_clean = re.sub(r"\b(ka|ki|ke|का|की|के)\b$", "", city_clean).strip()
    if not city_clean:
        return ""
    return " ".join(word.capitalize() for word in city_clean.split())


def _is_location_request_query(query: str) -> bool:
    """Check if user is asking for weather without specifying a city."""
    query_lower = query.lower().strip()

    # Simple weather queries without city (should request location)
    simple_patterns = [
        r"^weather\s*$",
        r"^weather\s+today\s*$",
        r"^weather\s+now\s*$",
        r"^weather\s+(near\s+me|here|for\s+my\s+location|at\s+my\s+location)\s*\??$",  # Location-based
        r"^weather\s+(nearby|around\s+me)\s*\??$",  # Location-based
        r"^what('?s| is)\s+(the\s+)?weather\s*(today|now|near\s+me|here)?\s*\??$",
        r"^how('?s| is)\s+(the\s+)?weather\s*(today|now|near\s+me|here)?\s*\??$",
        r"^today('?s)?\s+weather\s*$",
        r"^current\s+weather\s*$",
        r"^temperature\s*(today|now|near\s+me|here)?\s*$",
        r"^what('?s| is)\s+(the\s+)?temperature\s*(today|now|near\s+me|here)?\s*\??$",
        r"^aaj\s+ka\s+mausam\s*$",  # Hindi: today's weather
        r"^mausam\s*$",  # Hindi: weather
        r"^mausam\s+kaisa\s+hai\s*\??$",  # Hindi: how's the weather
        r"^mere\s+paas\s+(ka\s+)?mausam\s*$",  # Hindi: weather near me
        r"^yahan\s+ka\s+mausam\s*$",  # Hindi: weather here
    ]

    for pattern in simple_patterns:
        if re.match(pattern, query_lower):
            return True

    return False


# Weather description translations
WEATHER_DESCRIPTIONS = {
    "en": {
        "clear sky": "Clear Sky", "few clouds": "Few Clouds", "scattered clouds": "Scattered Clouds",
        "broken clouds": "Broken Clouds", "overcast clouds": "Overcast Clouds",
        "light rain": "Light Rain", "moderate rain": "Moderate Rain", "heavy rain": "Heavy Rain",
        "thunderstorm": "Thunderstorm", "snow": "Snow", "mist": "Mist", "fog": "Fog",
        "haze": "Haze", "smoke": "Smoke", "dust": "Dust", "drizzle": "Drizzle",
    },
    "hi": {
        "clear sky": "साफ आसमान", "few clouds": "कुछ बादल", "scattered clouds": "बिखरे बादल",
        "broken clouds": "टूटे बादल", "overcast clouds": "घने बादल",
        "light rain": "हल्की बारिश", "moderate rain": "मध्यम बारिश", "heavy rain": "भारी बारिश",
        "thunderstorm": "आंधी-तूफान", "snow": "बर्फबारी", "mist": "कोहरा", "fog": "घना कोहरा",
        "haze": "धुंध", "smoke": "धुआं", "dust": "धूल", "drizzle": "बूंदाबांदी",
    },
    "bn": {
        "clear sky": "পরিষ্কার আকাশ", "few clouds": "কিছু মেঘ", "scattered clouds": "ছড়িয়ে থাকা মেঘ",
        "broken clouds": "ভাঙা মেঘ", "overcast clouds": "ঘন মেঘ",
        "light rain": "হালকা বৃষ্টি", "moderate rain": "মাঝারি বৃষ্টি", "heavy rain": "ভারী বৃষ্টি",
        "thunderstorm": "বজ্রঝড়", "snow": "তুষারপাত", "mist": "কুয়াশা", "fog": "ঘন কুয়াশা",
        "haze": "ধোঁয়াশা", "smoke": "ধোঁয়া", "dust": "ধুলো", "drizzle": "গুঁড়িগুঁড়ি বৃষ্টি",
    },
    "ta": {
        "clear sky": "தெளிவான வானம்", "few clouds": "சில மேகங்கள்", "scattered clouds": "சிதறிய மேகங்கள்",
        "broken clouds": "உடைந்த மேகங்கள்", "overcast clouds": "மேகமூட்டம்",
        "light rain": "லேசான மழை", "moderate rain": "மிதமான மழை", "heavy rain": "கனமழை",
        "thunderstorm": "இடியுடன் மழை", "snow": "பனிப்பொழிவு", "mist": "மூடுபனி", "fog": "அடர் மூடுபனி",
        "haze": "புகை மூட்டம்", "smoke": "புகை", "dust": "தூசி", "drizzle": "தூறல்",
    },
    "te": {
        "clear sky": "స్వచ్ఛమైన ఆకాశం", "few clouds": "కొన్ని మేఘాలు", "scattered clouds": "చెల్లాచెదురు మేఘాలు",
        "broken clouds": "విరిగిన మేఘాలు", "overcast clouds": "మేఘావృతం",
        "light rain": "తేలికపాటి వర్షం", "moderate rain": "మధ్యస్థ వర్షం", "heavy rain": "భారీ వర్షం",
        "thunderstorm": "ఉరుములతో వర్షం", "snow": "మంచు", "mist": "పొగమంచు", "fog": "దట్టమైన పొగమంచు",
        "haze": "మసక", "smoke": "పొగ", "dust": "దుమ్ము", "drizzle": "జల్లు",
    },
    "kn": {
        "clear sky": "ನಿರಭ್ರ ಆಕಾಶ", "few clouds": "ಕೆಲವು ಮೋಡಗಳು", "scattered clouds": "ಹರಡಿದ ಮೋಡಗಳು",
        "broken clouds": "ಒಡೆದ ಮೋಡಗಳು", "overcast clouds": "ಮೋಡ ಕವಿದ",
        "light rain": "ಹಗುರ ಮಳೆ", "moderate rain": "ಮಧ್ಯಮ ಮಳೆ", "heavy rain": "ಭಾರೀ ಮಳೆ",
        "thunderstorm": "ಗುಡುಗು ಸಹಿತ ಮಳೆ", "snow": "ಹಿಮಪಾತ", "mist": "ಮಂಜು", "fog": "ದಟ್ಟ ಮಂಜು",
        "haze": "ಧೂಳು ಮಂಜು", "smoke": "ಹೊಗೆ", "dust": "ಧೂಳು", "drizzle": "ಸಣ್ಣ ಮಳೆ",
    },
    "ml": {
        "clear sky": "തെളിഞ്ഞ ആകാശം", "few clouds": "കുറച്ച് മേഘങ്ങൾ", "scattered clouds": "ചിതറിയ മേഘങ്ങൾ",
        "broken clouds": "പൊട്ടിയ മേഘങ്ങൾ", "overcast clouds": "മേഘാവൃതം",
        "light rain": "നേരിയ മഴ", "moderate rain": "മിതമായ മഴ", "heavy rain": "കനത്ത മഴ",
        "thunderstorm": "ഇടിമിന്നലോടെ മഴ", "snow": "മഞ്ഞുവീഴ്ച", "mist": "മൂടൽമഞ്ഞ്", "fog": "കടുത്ത മൂടൽമഞ്ഞ്",
        "haze": "പുകമഞ്ഞ്", "smoke": "പുക", "dust": "പൊടി", "drizzle": "ചാറ്റൽമഴ",
    },
    "gu": {
        "clear sky": "સાફ આકાશ", "few clouds": "થોડા વાદળો", "scattered clouds": "વિખરાયેલા વાદળો",
        "broken clouds": "તૂટેલા વાદળો", "overcast clouds": "ઘેરાયેલા વાદળો",
        "light rain": "હળવો વરસાદ", "moderate rain": "મધ્યમ વરસાદ", "heavy rain": "ભારે વરસાદ",
        "thunderstorm": "વીજળી સાથે વરસાદ", "snow": "બરફવર્ષા", "mist": "ઝાકળ", "fog": "ગાઢ ધુમ્મસ",
        "haze": "ધુમ્મસ", "smoke": "ધુમાડો", "dust": "ધૂળ", "drizzle": "ઝરમર",
    },
    "mr": {
        "clear sky": "स्वच्छ आकाश", "few clouds": "काही ढग", "scattered clouds": "विखुरलेले ढग",
        "broken clouds": "तुटलेले ढग", "overcast clouds": "दाट ढग",
        "light rain": "हलका पाऊस", "moderate rain": "मध्यम पाऊस", "heavy rain": "जोरदार पाऊस",
        "thunderstorm": "वादळी पाऊस", "snow": "बर्फवृष्टी", "mist": "धुके", "fog": "दाट धुके",
        "haze": "धूसर", "smoke": "धूर", "dust": "धूळ", "drizzle": "रिमझिम",
    },
    "pa": {
        "clear sky": "ਸਾਫ਼ ਅਸਮਾਨ", "few clouds": "ਕੁਝ ਬੱਦਲ", "scattered clouds": "ਖਿੱਲਰੇ ਬੱਦਲ",
        "broken clouds": "ਟੁੱਟੇ ਬੱਦਲ", "overcast clouds": "ਘਣੇ ਬੱਦਲ",
        "light rain": "ਹਲਕੀ ਬਾਰਸ਼", "moderate rain": "ਦਰਮਿਆਨੀ ਬਾਰਸ਼", "heavy rain": "ਭਾਰੀ ਬਾਰਸ਼",
        "thunderstorm": "ਗਰਜ ਨਾਲ ਬਾਰਸ਼", "snow": "ਬਰਫ਼ਬਾਰੀ", "mist": "ਧੁੰਦ", "fog": "ਸੰਘਣੀ ਧੁੰਦ",
        "haze": "ਧੁੰਦਲਾਪਨ", "smoke": "ਧੂੰਆਂ", "dust": "ਧੂੜ", "drizzle": "ਬੁੱਛਾੜ",
    },
    "or": {
        "clear sky": "ସଫା ଆକାଶ", "few clouds": "କିଛି ମେଘ", "scattered clouds": "ଛିଟାଛିଟି ମେଘ",
        "broken clouds": "ଭଙ୍ଗା ମେଘ", "overcast clouds": "ଘନ ମେଘ",
        "light rain": "ହାଲୁକା ବର୍ଷା", "moderate rain": "ମଧ୍ୟମ ବର୍ଷା", "heavy rain": "ଭାରୀ ବର୍ଷା",
        "thunderstorm": "ବଜ୍ରପାତ ସହ ବର୍ଷା", "snow": "ତୁଷାରପାତ", "mist": "କୁହୁଡ଼ି", "fog": "ଘନ କୁହୁଡ଼ି",
        "haze": "ଧୂଆଁ କୁହୁଡ଼ି", "smoke": "ଧୂଆଁ", "dust": "ଧୂଳି", "drizzle": "ହାଲୁକା ବୃଷ୍ଟି",
    },
}


def _translate_weather_description(description: str, lang: str) -> str:
    """Translate weather description to target language."""
    if lang == "en" or not description:
        return description

    desc_lower = description.lower()
    lang_descriptions = WEATHER_DESCRIPTIONS.get(lang, WEATHER_DESCRIPTIONS["en"])

    # Try exact match first
    if desc_lower in lang_descriptions:
        return lang_descriptions[desc_lower]

    # Try partial match
    for eng, translated in lang_descriptions.items():
        if eng in desc_lower:
            return translated

    return description  # Return original if no translation found


def _extract_number(value: str) -> float | None:
    if not value:
        return None
    match = re.search(r"(-?\d+(?:\.\d+)?)", value)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _build_weather_tips_hi(description: str, temperature: str, humidity: str, visibility: str) -> list[str]:
    tips = []
    desc_lower = (description or "").lower()
    temp_val = _extract_number(temperature)
    humidity_val = _extract_number(humidity)
    visibility_val = _extract_number(visibility)

    if any(word in desc_lower for word in ["rain", "drizzle", "thunderstorm"]):
        tips.append("छाता/रेनकोट साथ रखें।")
    if any(word in desc_lower for word in ["fog", "haze", "mist", "smoke", "dust"]):
        tips.append("कम दृश्यता हो सकती है, सावधानी रखें।")
    if visibility_val is not None and visibility_val <= 2.0:
        tips.append("ड्राइविंग करते समय धीमी गति रखें।")
    if temp_val is not None and temp_val >= 35:
        tips.append("गर्मी से बचने के लिए पानी अधिक पिएं।")
    if temp_val is not None and temp_val <= 12:
        tips.append("ठंड से बचने के लिए गर्म कपड़े पहनें।")
    if humidity_val is not None and humidity_val >= 70:
        tips.append("उमस ज्यादा हो सकती है, हल्के कपड़े पहनें।")

    if not tips:
        tips.append("मौसम के अनुसार हल्के और आरामदायक कपड़े पहनें।")

    return tips[:3]


def _build_weather_tips_en(description: str, temperature: str, humidity: str, visibility: str) -> list[str]:
    tips = []
    desc_lower = (description or "").lower()
    temp_val = _extract_number(temperature)
    humidity_val = _extract_number(humidity)
    visibility_val = _extract_number(visibility)

    if any(word in desc_lower for word in ["rain", "drizzle", "thunderstorm"]):
        tips.append("Carry an umbrella or raincoat.")
    if any(word in desc_lower for word in ["fog", "haze", "mist", "smoke", "dust"]):
        tips.append("Low visibility possible; stay cautious.")
    if visibility_val is not None and visibility_val <= 2.0:
        tips.append("Drive slowly in low visibility.")
    if temp_val is not None and temp_val >= 35:
        tips.append("Stay hydrated and avoid peak heat.")
    if temp_val is not None and temp_val <= 12:
        tips.append("Wear warm layers.")
    if humidity_val is not None and humidity_val >= 70:
        tips.append("It may feel humid; wear light clothing.")

    if not tips:
        tips.append("Dress comfortably for the weather.")

    return tips[:3]


def _format_weather_structured_en(data: dict, sources: list) -> str:
    location = data.get("location", "").strip() or "this location"
    description = data.get("description", "")
    temp = data.get("temperature", "N/A")
    feels_like = data.get("feels_like", "")
    humidity = data.get("humidity", "")
    wind_speed = data.get("wind_speed", "")
    visibility = data.get("visibility", "")
    pressure = data.get("pressure", "")
    sunrise = data.get("sunrise", "")
    sunset = data.get("sunset", "")

    lines = [
        f"Today's weather in {location}",
        f"{data.get('emoji', '')} {description}",
        "",
        "Conditions:",
        f"- Temperature: {temp} (Feels like {feels_like})" if feels_like else f"- Temperature: {temp}",
        f"- Humidity: {humidity}" if humidity else None,
        f"- Wind: {wind_speed}" if wind_speed else None,
        f"- Visibility: {visibility}" if visibility and visibility != "0.0 km" else None,
        f"- Pressure: {pressure}" if pressure else None,
    ]
    if sunrise and sunset:
        lines.append(f"- Sunrise: {sunrise} | Sunset: {sunset}")
    elif sunrise:
        lines.append(f"- Sunrise: {sunrise}")
    elif sunset:
        lines.append(f"- Sunset: {sunset}")

    lines = [line for line in lines if line]

    tips = _build_weather_tips_en(description, temp, humidity, visibility)
    if tips:
        lines.extend(["", "Tips:"])
        lines.extend([f"- {tip}" for tip in tips])

    if sources:
        source_links = []
        for idx, item in enumerate(sources[:3], start=1):
            link = item.get("link") or ""
            if link:
                source_links.append(f"{idx}. {link}")
        if source_links:
            lines.append("")
            lines.append("Sources:")
            lines.extend(source_links)
            lines.append("powered by web-search")

    return "\n".join(lines)


def _format_weather_response(data: dict, lang: str = "en") -> str:
    """Format weather data into a nice WhatsApp message with localized labels."""
    emoji = data.get("emoji", "")
    description = data.get("description", "")
    location = data["location"]

    # Translate weather description
    translated_description = _translate_weather_description(description, lang)

    # Get localized labels
    title = get_weather_label("title", lang, city=location)
    temp_label = get_weather_label("temp", lang)
    feels_label = get_weather_label("feels_like", lang)
    humidity_label = get_weather_label("humidity", lang)
    wind_label = get_weather_label("wind", lang)
    visibility_label = get_weather_label("visibility", lang)

    response_lines = [
        f"*{title}*\n",
        f"{emoji} *{translated_description}*\n",
        f"🌡️ {temp_label}: *{data['temperature']}*",
        f"🤔 {feels_label}: *{data['feels_like']}*",
        f"💧 {humidity_label}: *{data['humidity']}*",
        f"💨 {wind_label}: *{data['wind_speed']}*",
    ]

    # Add visibility if available
    visibility = data.get("visibility", "")
    if visibility and visibility != "0.0 km":
        response_lines.append(f"👁️ {visibility_label}: *{visibility}*")

    return "\n".join(response_lines)


def _format_weather_narrative_hi(data: dict, sources: list) -> str:
    location = data.get("location", "").strip() or "इस स्थान"
    description_raw = data.get("description", "")
    description = _translate_weather_description(description_raw, "hi")
    temp = data.get("temperature", "N/A")
    feels_like = data.get("feels_like", "")
    humidity = data.get("humidity", "")
    wind_speed = data.get("wind_speed", "")
    visibility = data.get("visibility", "")
    pressure = data.get("pressure", "")
    sunrise = data.get("sunrise", "")
    sunset = data.get("sunset", "")

    lines = [
        f"आज {location} का मौसम",
        f"{data.get('emoji', '')} {description}",
        "",
        "मौसम की स्थिति:",
        f"- तापमान: {temp} (महसूस {feels_like})" if feels_like else f"- तापमान: {temp}",
        f"- नमी: {humidity}" if humidity else None,
        f"- हवा: {wind_speed}" if wind_speed else None,
        f"- दृश्यता: {visibility}" if visibility and visibility != "0.0 km" else None,
        f"- वायुदाब: {pressure}" if pressure else None,
    ]
    if sunrise and sunset:
        lines.append(f"- सूर्योदय: {sunrise} | सूर्यास्त: {sunset}")
    elif sunset:
        lines.append(f"- सूर्यास्त: {sunset}")
    elif sunrise:
        lines.append(f"- सूर्योदय: {sunrise}")

    lines = [line for line in lines if line]

    tips = _build_weather_tips_hi(description_raw, temp, humidity, visibility)
    if tips:
        lines.extend(["", "सुझाव:"])
        lines.extend([f"- {tip}" for tip in tips])

    if sources:
        source_links = []
        for idx, item in enumerate(sources[:3], start=1):
            link = item.get("link") or ""
            if link:
                source_links.append(f"{idx}. {link}")
        if source_links:
            lines.append("")
            lines.append("स्रोत:")
            lines.extend(source_links)
            lines.append("powered by web-search")

    return "\n".join(lines)


async def _fetch_weather_sources(city: str) -> list:
    if not city:
        return []
    search_query = f"{city} weather today".strip()
    sources_result = await search_google(query=search_query, max_results=5, country="in", locale="en")
    if not sources_result.get("success"):
        return []
    return (sources_result.get("data") or {}).get("results", []) or []


async def _format_weather_response_hi(data: dict, city: str) -> str:
    sources = await _fetch_weather_sources(city)
    return _format_weather_narrative_hi(data, sources)


async def _format_weather_response_structured(data: dict, city: str, lang: str = "en") -> str:
    """
    Format weather data using a structured template for all languages.
    """
    sources = await _fetch_weather_sources(city)
    response_en = _format_weather_structured_en(data, sources)
    if lang == "en":
        return response_en
    if AI_TRANSLATE_AVAILABLE:
        try:
            return await ai_translate_response(
                text=response_en,
                target_language=lang,
                openai_api_key=settings.openai_api_key
            )
        except Exception as e:
            logger.warning(f"AI translation failed, using English: {e}")
    return response_en


async def handle_weather(state: BotState) -> dict:
    """
    Node function: Get current weather for a city or location.
    Returns response in user's detected language.

    Supports two flows:
    1. Direct weather with city (e.g., "weather in Delhi")
    2. Weather without city - asks for WhatsApp location, then shows weather

    Args:
        state: Current bot state with query containing city name.

    Returns:
        Updated state with weather information or location request.
    """
    entities = state.get("extracted_entities", {})
    whatsapp_message = state.get("whatsapp_message", {})
    phone = whatsapp_message.get("from_number", "")
    location_data = whatsapp_message.get("location")
    message_type = whatsapp_message.get("message_type", "text")
    detected_lang = state.get("detected_language", "en")

    logger.info(f"handle_weather called: phone={phone}, message_type={message_type}, location_data={location_data}")

    pending_store = get_pending_location_store()

    # Check if user sent a location (responding to our location request for weather)
    if location_data and message_type == "location":
        logger.info(f"Location message received from {phone}, checking for pending weather request")
        pending = await pending_store.get_pending_search(phone)
        logger.info(f"Pending search result: {pending}")

        if pending and pending.get("search_query") == "__weather__":
            # User sent location for weather
            lat = location_data.get("latitude")
            lon = location_data.get("longitude")

            logger.info(f"Processing weather with location: {lat},{lon}")

            # Send acknowledgment message before processing (localized)
            try:
                whatsapp_client = get_whatsapp_client()
                wait_msg = get_phrase("please_wait", detected_lang)
                await whatsapp_client.send_text_message(
                    to=phone,
                    text=f"🌤️ {wait_msg}"
                )
            except Exception as e:
                logger.warning(f"Failed to send acknowledgment: {e}")

            return await _execute_weather_with_coordinates(lat, lon, detected_lang)

    # Try to get city from entities first, then extract from query
    city = _normalize_city_name(entities.get("city", ""))
    query = state.get("current_query", "")

    # FIRST check if this is a simple weather query without city - ask for location
    # This must come BEFORE trying to extract city to avoid false extractions
    if not city and _is_location_request_query(query):
        # Save pending weather request
        await pending_store.save_pending_search(
            phone=phone,
            search_query="__weather__",  # Special marker for weather
            original_message=query,
        )

        # Request location from user (localized)
        ask_city = get_weather_label("ask_city", detected_lang)
        return {
            "response_text": ask_city,
            "response_type": RESPONSE_TYPE_LOCATION_REQUEST,
            "should_fallback": False,
            "intent": INTENT,
        }

    # If city not in entities, try to extract from query
    if not city:
        city = _normalize_city_name(_extract_city_from_query(query))

    if not city:
        # Localized error message
        ask_city = get_weather_label("ask_city", detected_lang)
        examples_label = get_weather_label("examples", detected_lang)
        return {
            "response_text": (
                f"*{get_weather_label('title', detected_lang, city='').replace(' में ', '').replace(' in ', '').strip()}*\n\n"
                f"{ask_city}\n\n"
                f"*{examples_label}:*\n"
                "- Weather in Delhi\n"
                "- दिल्ली में मौसम\n"
                "- Chennai weather"
            ),
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    try:
        result = get_weather(city)

        if result["success"]:
            data = result["data"]
            if detected_lang == "hi":
                response_text = await _format_weather_response_hi(data, city)
            else:
                response_text = await _format_weather_response_structured(data, city, detected_lang)
            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }
        else:
            raw_error = result.get("error", "")
            user_message = sanitize_error(raw_error, "weather")
            error_msg = get_weather_label("error", detected_lang, city=city)
            return {
                "tool_result": result,
                "response_text": error_msg,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

    except Exception as e:
        logger.error(f"Weather handler error: {e}")
        error_msg = get_phrase("error_occurred", detected_lang)
        return {
            "response_text": error_msg,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }


async def _execute_weather_with_coordinates(latitude: float, longitude: float, lang: str = "en") -> dict:
    """
    Execute weather lookup using coordinates.

    Args:
        latitude: User's latitude
        longitude: User's longitude
        lang: Language code for response

    Returns:
        Response dict with weather data
    """
    try:
        result = get_weather_by_coordinates(latitude, longitude)

        if result["success"]:
            data = result["data"]
            if lang == "hi":
                response_text = await _format_weather_response_hi(data, data.get("location", ""))
            else:
                response_text = await _format_weather_response_structured(data, data.get("location", ""), lang)
            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }
        else:
            raw_error = result.get("error", "")
            user_message = sanitize_error(raw_error, "weather")
            error_msg = get_phrase("error_occurred", lang)
            return {
                "tool_result": result,
                "response_text": error_msg,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

    except Exception as e:
        logger.error(f"Weather with coordinates error: {e}")
        error_msg = get_phrase("error_occurred", lang)
        return {
            "response_text": error_msg,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
