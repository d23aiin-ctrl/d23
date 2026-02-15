"""
Kundli (Birth Chart) Node - Enhanced Version

Generates complete Vedic birth charts with:
1. Accurate planetary calculations (Swiss Ephemeris)
2. Beautiful Hindi/English formatting
3. Detailed life predictions
4. Multi-language support (11+ Indian languages)
5. Web-enhanced astrological insights
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from common.graph.state import BotState
from common.tools.astro_tool import calculate_kundli
from common.tools.serper_search import search_google
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from common.config import settings

logger = logging.getLogger(__name__)

INTENT = "birth_chart"

# Language names for translation
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

# Sign names in Hindi
SIGN_HINDI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन",
    "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
    "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
    "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}


async def get_enhanced_interpretation(
    kundli_data: Dict,
    detected_lang: str = "hi"
) -> str:
    """
    Get enhanced astrological interpretation using web search and LLM.

    Args:
        kundli_data: Birth chart data from calculate_kundli
        detected_lang: User's language preference

    Returns:
        Enhanced interpretation text
    """
    try:
        sun_sign = kundli_data.get("sun_sign", "")
        moon_sign = kundli_data.get("moon_sign", "")
        moon_nakshatra = kundli_data.get("moon_nakshatra", "")
        ascendant = kundli_data.get("ascendant", {}).get("sign", "")

        # Search for astrological insights
        search_query = (
            f"{sun_sign} sun {moon_sign} moon {ascendant} ascendant {moon_nakshatra} nakshatra "
            f"vedic astrology personality career life predictions"
        )

        search_result = await search_google(query=search_query, max_results=5, country="in")

        # Prepare context for LLM
        context = ""
        if search_result.get("success") and search_result.get("data"):
            results = search_result["data"].get("results", [])
            for i, result in enumerate(results[:3], 1):
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                context += f"Source {i}:\nTitle: {title}\nContent: {snippet}\n\n"

        # Use LLM to generate interpretation
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            api_key=settings.OPENAI_API_KEY
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Vedic astrologer providing detailed life predictions based on birth charts."),
            ("user", """Based on the following birth chart details and astrological knowledge, provide a comprehensive interpretation in {language}:

Birth Chart Details:
- Sun Sign: {sun_sign}
- Moon Sign: {moon_sign}
- Moon Nakshatra: {moon_nakshatra}
- Ascendant (Lagna): {ascendant}
- Varna: {varna}
- Gana: {gana}

Web Research Context:
{context}

Instructions:
1. Write in {language} language
2. Provide insights on:
   - Personality & Nature (स्वभाव)
   - Career & Professional Life (करियर)
   - Relationships & Marriage (संबंध)
   - Health & Well-being (स्वास्थ्य)
   - Lucky Elements (भाग्यशाली तत्व)
3. Make it narrative, positive, and practical
4. Use traditional Vedic astrology principles
5. Keep it concise (3-4 sentences per section)

Format in beautiful narrative style with clear sections.""")
        ])

        chain = prompt | llm
        result = await chain.ainvoke({
            "language": "Hindi" if detected_lang == "hi" else "English",
            "sun_sign": sun_sign,
            "moon_sign": moon_sign,
            "moon_nakshatra": moon_nakshatra,
            "ascendant": ascendant,
            "varna": kundli_data.get("varna", "Unknown"),
            "gana": kundli_data.get("gana", "Unknown"),
            "context": context if context else "Use traditional Vedic astrology knowledge"
        })

        return result.content.strip()

    except Exception as e:
        logger.error(f"Enhanced interpretation failed: {e}")
        return ""


async def format_kundli_hindi(kundli_data: Dict, interpretation: str = "") -> str:
    """Format kundli in beautiful Hindi style."""
    lines = []

    # Header
    name = kundli_data.get("name", "")
    if name:
        lines.append(f"🔮 *{name} की कुंडली*")
    else:
        lines.append("🔮 *जन्म कुंडली*")
    lines.append("")

    # Birth details
    lines.append("*जन्म विवरण:*")
    birth_date = kundli_data.get("birth_date", "")
    birth_time = kundli_data.get("birth_time", "")
    birth_place = kundli_data.get("birth_place", "")

    if birth_date:
        lines.append(f"📅 जन्म तिथि: {birth_date}")
    if birth_time:
        lines.append(f"🕐 जन्म समय: {birth_time}")
    if birth_place:
        lines.append(f"📍 जन्म स्थान: {birth_place}")
    lines.append("")

    # Main chart details
    lines.append("*मुख्य ग्रह स्थितियाँ:*")

    ascendant = kundli_data.get("ascendant", {})
    if ascendant:
        sign = ascendant.get("sign", "")
        sign_hi = SIGN_HINDI.get(sign, sign)
        lines.append(f"🌅 लग्न (Ascendant): {sign_hi} ({sign})")

    sun_sign = kundli_data.get("sun_sign", "")
    if sun_sign:
        sun_hi = SIGN_HINDI.get(sun_sign, sun_sign)
        lines.append(f"☀️ सूर्य राशि: {sun_hi} ({sun_sign})")

    moon_sign = kundli_data.get("moon_sign", "")
    if moon_sign:
        moon_hi = SIGN_HINDI.get(moon_sign, moon_sign)
        lines.append(f"🌙 चंद्र राशि: {moon_hi} ({moon_sign})")

    moon_nakshatra = kundli_data.get("moon_nakshatra", "")
    if moon_nakshatra:
        lines.append(f"⭐ नक्षत्र: {moon_nakshatra}")

    lines.append("")

    # Vedic attributes
    lines.append("*वैदिक गुण:*")
    varna = kundli_data.get("varna", "")
    nadi = kundli_data.get("nadi", "")
    yoni = kundli_data.get("yoni", "")
    gana = kundli_data.get("gana", "")
    vashya = kundli_data.get("vashya", "")

    if varna:
        lines.append(f"• वर्ण: {varna}")
    if gana:
        lines.append(f"• गण: {gana}")
    if nadi:
        lines.append(f"• नाड़ी: {nadi}")
    if yoni:
        lines.append(f"• योनि: {yoni}")
    if vashya:
        lines.append(f"• वश्य: {vashya}")

    lines.append("")

    # Planetary positions
    planetary_positions = kundli_data.get("planetary_positions", {})
    if planetary_positions:
        lines.append("*ग्रहों की स्थिति:*")
        planet_names_hi = {
            "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल",
            "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र",
            "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
        }

        for planet, info in planetary_positions.items():
            planet_hi = planet_names_hi.get(planet, planet)
            sign = info.get("sign", "")
            sign_hi = SIGN_HINDI.get(sign, sign)
            nakshatra = info.get("nakshatra", "")
            lines.append(f"• {planet_hi}: {sign_hi} राशि, {nakshatra} नक्षत्र")

        lines.append("")

    # Enhanced interpretation
    if interpretation:
        lines.append("*विस्तृत विश्लेषण:*")
        lines.append(interpretation)
        lines.append("")

    # Footer
    lines.append("_✨ Swiss Ephemeris गणना पर आधारित_")
    lines.append("_🌐 powered by web-enhanced astrology_")

    return "\n".join(lines)


async def format_kundli_english(kundli_data: Dict, interpretation: str = "") -> str:
    """Format kundli in English style."""
    lines = []

    # Header
    name = kundli_data.get("name", "")
    if name:
        lines.append(f"🔮 *Birth Chart for {name}*")
    else:
        lines.append("🔮 *Birth Chart (Kundli)*")
    lines.append("")

    # Birth details
    lines.append("*Birth Details:*")
    birth_date = kundli_data.get("birth_date", "")
    birth_time = kundli_data.get("birth_time", "")
    birth_place = kundli_data.get("birth_place", "")

    if birth_date:
        lines.append(f"📅 Birth Date: {birth_date}")
    if birth_time:
        lines.append(f"🕐 Birth Time: {birth_time}")
    if birth_place:
        lines.append(f"📍 Birth Place: {birth_place}")
    lines.append("")

    # Main chart details
    lines.append("*Main Positions:*")

    ascendant = kundli_data.get("ascendant", {})
    if ascendant:
        sign = ascendant.get("sign", "")
        lines.append(f"🌅 Ascendant (Lagna): {sign}")

    sun_sign = kundli_data.get("sun_sign", "")
    if sun_sign:
        lines.append(f"☀️ Sun Sign: {sun_sign}")

    moon_sign = kundli_data.get("moon_sign", "")
    if moon_sign:
        lines.append(f"🌙 Moon Sign: {moon_sign}")

    moon_nakshatra = kundli_data.get("moon_nakshatra", "")
    if moon_nakshatra:
        lines.append(f"⭐ Nakshatra: {moon_nakshatra}")

    lines.append("")

    # Vedic attributes
    lines.append("*Vedic Attributes:*")
    varna = kundli_data.get("varna", "")
    nadi = kundli_data.get("nadi", "")
    yoni = kundli_data.get("yoni", "")
    gana = kundli_data.get("gana", "")
    vashya = kundli_data.get("vashya", "")

    if varna:
        lines.append(f"• Varna: {varna}")
    if gana:
        lines.append(f"• Gana: {gana}")
    if nadi:
        lines.append(f"• Nadi: {nadi}")
    if yoni:
        lines.append(f"• Yoni: {yoni}")
    if vashya:
        lines.append(f"• Vashya: {vashya}")

    lines.append("")

    # Planetary positions
    planetary_positions = kundli_data.get("planetary_positions", {})
    if planetary_positions:
        lines.append("*Planetary Positions:*")

        for planet, info in planetary_positions.items():
            sign = info.get("sign", "")
            nakshatra = info.get("nakshatra", "")
            lines.append(f"• {planet}: {sign}, {nakshatra} Nakshatra")

        lines.append("")

    # Enhanced interpretation
    if interpretation:
        lines.append("*Detailed Analysis:*")
        lines.append(interpretation)
        lines.append("")

    # Footer
    lines.append("_✨ Based on Swiss Ephemeris calculations_")
    lines.append("_🌐 powered by web-enhanced astrology_")

    return "\n".join(lines)


async def translate_to_language(text: str, lang_code: str) -> str:
    """Translate kundli response to target language."""
    if lang_code in ["en", "hi"] or lang_code not in LANGUAGE_NAMES:
        return text

    try:
        lang_info = LANGUAGE_NAMES.get(lang_code, {})
        language_name = lang_info.get("en", lang_code)
        native_name = lang_info.get("native", language_name)

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional translator specialized in Indian languages and astrology terminology."),
            ("user", """Translate the following birth chart (kundli) information to {language_name} ({native_name}).

Original text:
{text}

Instructions:
1. Translate to {language_name} while preserving:
   - Astrological terms accuracy
   - Formatting (bold, emojis, sections)
   - Names of planets, signs, nakshatras
2. Keep English terms in brackets for clarity
3. Maintain the same structure and sections

Return ONLY the translated text.""")
        ])

        chain = prompt | llm
        result = await chain.ainvoke({
            "text": text,
            "language_name": language_name,
            "native_name": native_name,
        })

        return result.content.strip()
    except Exception as e:
        logger.warning(f"Translation failed for {lang_code}: {e}")
        return text


async def handle_birth_chart(state: BotState) -> dict:
    """
    Handle birth chart (Kundli) generation with enhanced formatting and interpretation.

    Features:
    - Accurate Swiss Ephemeris calculations
    - Beautiful Hindi/English formatting
    - Web-enhanced astrological insights
    - Multi-language support (11+ Indian languages)
    """
    entities = state.get("extracted_entities", {})
    birth_date = entities.get("birth_date", "").strip()
    birth_time = entities.get("birth_time", "").strip()
    birth_place = entities.get("birth_place", "").strip()
    name = entities.get("name", "").strip()
    detected_lang = state.get("detected_language", "hi")

    # Check required fields
    missing = []
    if not birth_date:
        missing.append("जन्म तिथि (birth date) - जैसे: 15-08-1990")
    if not birth_time:
        missing.append("जन्म समय (birth time) - जैसे: 10:30 AM")
    if not birth_place:
        missing.append("जन्म स्थान (birth place) - जैसे: Delhi")

    if missing:
        if detected_lang == "hi":
            return {
                "response_text": f"🔮 *जन्म कुंडली*\n\nकुंडली बनाने के लिए मुझे चाहिए:\n\n" +
                               "\n".join([f"✗ {field}" for field in missing]) +
                               "\n\n*उदाहरण:*\n\"राहुल की कुंडली बनाओ, जन्म 15-08-1990, समय 10:30 AM, स्थान Delhi\"",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }
        else:
            return {
                "response_text": f"🔮 *Birth Chart (Kundli)*\n\nTo generate your Kundli, I need:\n\n" +
                               "\n".join([f"✗ {field}" for field in missing]) +
                               "\n\n*Example:*\n\"Generate kundli for Rahul born on 15-08-1990 at 10:30 AM in Delhi\"",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

    try:
        # Calculate kundli using Swiss Ephemeris
        result = await calculate_kundli(
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            name=name if name else None
        )

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            return {
                "tool_result": result,
                "response_text": f"⚠️ कुंडली बनाने में त्रुटि: {error_msg}\n\nकृपया सही विवरण दें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        kundli_data = result.get("data", {})

        # Add user-provided details to kundli_data
        kundli_data["name"] = name
        kundli_data["birth_date"] = birth_date
        kundli_data["birth_time"] = birth_time
        kundli_data["birth_place"] = birth_place

        # Get enhanced interpretation
        interpretation = await get_enhanced_interpretation(kundli_data, detected_lang)

        # Format based on language
        if detected_lang == "hi":
            response_text = await format_kundli_hindi(kundli_data, interpretation)
        else:
            response_text = await format_kundli_english(kundli_data, interpretation)

        # Translate to other Indian languages if needed
        if detected_lang not in ["en", "hi"]:
            response_text = await translate_to_language(response_text, detected_lang)

        return {
            "tool_result": result,
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Birth chart generation failed: {e}")
        return {
            "error": str(e),
            "response_text": "⚠️ कुंडली बनाने में त्रुटि हुई। कृपया पुनः प्रयास करें।",
            "response_type": "text",
            "should_fallback": True,
            "intent": INTENT,
        }


__all__ = ['handle_birth_chart', 'INTENT']
