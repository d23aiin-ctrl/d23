"""
Horoscope (Rashifal) Node

Fetches real-time daily horoscope from the internet and formats beautifully in multiple languages.
Fetches from popular Indian astrology websites and formats in narrative Hindi style.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from common.graph.state import BotState
from common.tools.serper_search import search_google
from common.utils.response_formatter import sanitize_error
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from common.config import settings

logger = logging.getLogger(__name__)

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

INTENT = "get_horoscope"

# Zodiac sign mappings
ZODIAC_SIGNS_EN_TO_HI = {
    "aries": "मेष",
    "taurus": "वृषभ",
    "gemini": "मिथुन",
    "cancer": "कर्क",
    "leo": "सिंह",
    "virgo": "कन्या",
    "libra": "तुला",
    "scorpio": "वृश्चिक",
    "sagittarius": "धनु",
    "capricorn": "मकर",
    "aquarius": "कुंभ",
    "pisces": "मीन",
}

ZODIAC_SIGNS_HI_TO_EN = {v: k for k, v in ZODIAC_SIGNS_EN_TO_HI.items()}

# English names for search
ZODIAC_SIGNS_ENGLISH = {
    "mesh": "aries",
    "vrishabh": "taurus",
    "mithun": "gemini",
    "kark": "cancer",
    "singh": "leo",
    "kanya": "virgo",
    "tula": "libra",
    "vrishchik": "scorpio",
    "dhanu": "sagittarius",
    "makar": "capricorn",
    "kumbh": "aquarius",
    "meen": "pisces",
}

# Lucky colors in Hindi
LUCKY_COLORS_HI = {
    "red": "लाल",
    "green": "हरा",
    "yellow": "पीला",
    "blue": "नीला",
    "white": "सफेद",
    "black": "काला",
    "orange": "नारंगी",
    "purple": "बैंगनी",
    "pink": "गुलाबी",
    "brown": "भूरा",
    "grey": "स्लेटी",
    "cream": "क्रीम",
    "golden": "सुनहरा",
    "silver": "चांदी",
}


def _normalize_sign(sign: str) -> Optional[str]:
    """Normalize zodiac sign to English lowercase."""
    sign_lower = sign.lower().strip()

    # Check if it's already English
    if sign_lower in ZODIAC_SIGNS_EN_TO_HI:
        return sign_lower

    # Check Hindi names
    if sign in ZODIAC_SIGNS_HI_TO_EN:
        return ZODIAC_SIGNS_HI_TO_EN[sign]

    # Check romanized Hindi names
    if sign_lower in ZODIAC_SIGNS_ENGLISH:
        return ZODIAC_SIGNS_ENGLISH[sign_lower]

    # Partial match
    for eng_sign in ZODIAC_SIGNS_EN_TO_HI.keys():
        if eng_sign.startswith(sign_lower[:3]):
            return eng_sign

    return None


def _extract_horoscope_info(result: Dict, sign_en: str) -> Dict:
    """Extract horoscope information from search result."""
    title = result.get("title", "").strip()
    snippet = result.get("snippet", "").strip()
    link = result.get("link", "").strip()

    text = f"{title} {snippet}"

    # Extract predictions/content
    prediction_patterns = [
        r'आज[\s\S]{100,800}',  # Long Hindi text
        r'Today[\s\S]{100,800}',  # Long English text
    ]

    predictions = []
    for pattern in prediction_patterns:
        matches = re.findall(pattern, text)
        predictions.extend(matches)

    # Extract lucky color
    lucky_color = ""
    color_pattern = re.compile(r'(?:lucky\s+color|शुभ\s+रंग)[\s:]*(\w+)', re.IGNORECASE)
    color_match = color_pattern.search(text)
    if color_match:
        lucky_color = color_match.group(1).strip()

    # Extract lucky number
    lucky_number = ""
    number_pattern = re.compile(r'(?:lucky\s+number|शुभ\s+अंक)[\s:]*(\d+)', re.IGNORECASE)
    number_match = number_pattern.search(text)
    if number_match:
        lucky_number = number_match.group(1).strip()

    # Extract advice/tip
    advice = ""
    advice_patterns = [
        r'(?:सलाह|advice)[\s:]*([^।\.\n]{20,200})',
        r'(?:tip|टिप)[\s:]*([^।\.\n]{20,200})',
    ]
    for pattern in advice_patterns:
        advice_match = re.search(pattern, text, re.IGNORECASE)
        if advice_match:
            advice = advice_match.group(1).strip()
            break

    return {
        "title": title,
        "snippet": snippet[:300],
        "link": link,
        "predictions": predictions,
        "lucky_color": lucky_color,
        "lucky_number": lucky_number,
        "advice": advice,
    }


def format_horoscope_hindi(sign_hi: str, sign_en: str, search_results: List[Dict]) -> str:
    """Format horoscope in beautiful Hindi narrative style."""
    lines = []

    # Date header
    current_date = datetime.now().strftime("%d %B %Y")
    # Convert to Hindi month
    month_map = {
        "January": "जनवरी", "February": "फरवरी", "March": "मार्च",
        "April": "अप्रैल", "May": "मई", "June": "जून",
        "July": "जुलाई", "August": "अगस्त", "September": "सितंबर",
        "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
    }
    for eng, hin in month_map.items():
        current_date = current_date.replace(eng, hin)

    lines.append(f"🔮 *आज के राशिफल विवरण ({current_date})*")
    lines.append("")

    # Extract horoscope info from results
    horoscope_data = []
    for result in search_results[:5]:
        info = _extract_horoscope_info(result, sign_en)
        if info["snippet"] or info["predictions"]:
            horoscope_data.append(info)

    if horoscope_data:
        # Main prediction (narrative style)
        first_result = horoscope_data[0]

        # Generate narrative introduction
        lines.append(f"आज, {current_date}, *{sign_hi} राशि* वालों के लिए दिन मिलाजुला रहेगा।")
        lines.append("")

        # Main horoscope content (combine snippets)
        main_content = []
        for data in horoscope_data[:2]:
            if data["snippet"]:
                # Clean up snippet
                clean_snippet = data["snippet"].replace("...", "").replace("  ", " ").strip()
                if len(clean_snippet) > 50:
                    main_content.append(clean_snippet)

        if main_content:
            combined_text = " ".join(main_content[:2])
            # Split into sentences and take first few
            sentences = re.split(r'[।\.]', combined_text)
            good_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:4]
            lines.append(" ".join(good_sentences[:3]) + "।")
            lines.append("")

        # Professional life section
        lines.append("*पेशेवर जीवन में:*")
        lines.append("आज आपका मन लोगों से घुलने-मिलने को करेगा। नौकरीपेशा लोगों को सहकर्मियों के साथ तालमेल बनाए रखना होगा। व्यापार में सफलता मिलेगी।")
        lines.append("")

        # Love life section
        lines.append("*प्रेम जीवन:*")
        lines.append("आज आपका मन लोगों से घुलने-मिलने को करेगा। अगर आप किसी के साथ रिश्ते में हैं, तो एक साधारण आउटिंग रिश्ते को मजबूत बना सकती है।")
        lines.append("")

        # Lucky details
        lucky_color = first_result.get("lucky_color", "क्रीम")
        lucky_number = first_result.get("lucky_number", "")
        advice = first_result.get("advice", "धन का दान करें और आज छोटे-छोटे आइडिया को एक्सप्लोर करें।")

        # Translate lucky color to Hindi if English
        lucky_color_display = LUCKY_COLORS_HI.get(lucky_color.lower(), lucky_color)

        lines.append(f"*शुभ रंग:* {lucky_color_display}")
        if lucky_number:
            lines.append(f"*शुभ अंक:* {lucky_number}")
        lines.append(f"*सलाह:* {advice}")
        lines.append("")

        # Sources
        lines.append("*स्रोत:*")
        source_count = 0
        for data in horoscope_data[:3]:
            if data["link"]:
                source_count += 1
                source_name = "आज तक" if "aajtak" in data["link"] else "नवभारत टाइम्स" if "navbharat" in data["link"] else "ज्योतिष"
                lines.append(f"स्रोत {source_count} [ {data['link']} ]")

    else:
        lines.append(f"इस समय {sign_hi} राशि के लिए राशिफल उपलब्ध नहीं है।")
        lines.append("")

    lines.append("")
    lines.append("🌐 _powered by web-search_")

    return "\n".join(lines)


def format_horoscope_english(sign_en: str, search_results: List[Dict]) -> str:
    """Format horoscope in English."""
    lines = []

    # Date header
    current_date = datetime.now().strftime("%d %B %Y")

    lines.append(f"🔮 *{sign_en.capitalize()} Daily Horoscope ({current_date})*")
    lines.append("")

    # Extract horoscope info from results
    horoscope_data = []
    for result in search_results[:5]:
        info = _extract_horoscope_info(result, sign_en)
        if info["snippet"] or info["predictions"]:
            horoscope_data.append(info)

    if horoscope_data:
        # Main prediction
        first_result = horoscope_data[0]

        lines.append(f"Today, {current_date}, will be a mixed day for *{sign_en.capitalize()}* natives.")
        lines.append("")

        # Main content
        main_content = []
        for data in horoscope_data[:2]:
            if data["snippet"]:
                clean_snippet = data["snippet"].replace("...", "").replace("  ", " ").strip()
                if len(clean_snippet) > 50:
                    main_content.append(clean_snippet)

        if main_content:
            combined_text = " ".join(main_content[:2])
            sentences = re.split(r'[\.]', combined_text)
            good_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:4]
            lines.append(" ".join(good_sentences[:3]) + ".")
            lines.append("")

        # Professional life
        lines.append("*Professional Life:*")
        lines.append("Today you will feel like socializing with people. Working professionals need to maintain coordination with colleagues. Success in business.")
        lines.append("")

        # Love life
        lines.append("*Love Life:*")
        lines.append("Today you will want to meet people. If you are in a relationship, a simple outing can strengthen the bond.")
        lines.append("")

        # Lucky details
        lucky_color = first_result.get("lucky_color", "Cream")
        lucky_number = first_result.get("lucky_number", "")
        advice = first_result.get("advice", "Donate and explore small ideas today.")

        lines.append(f"*Lucky Color:* {lucky_color.capitalize()}")
        if lucky_number:
            lines.append(f"*Lucky Number:* {lucky_number}")
        lines.append(f"*Advice:* {advice}")
        lines.append("")

        # Sources
        lines.append("*Sources:*")
        source_count = 0
        for data in horoscope_data[:3]:
            if data["link"]:
                source_count += 1
                source_name = "Aaj Tak" if "aajtak" in data["link"] else "Navbharat Times" if "navbharat" in data["link"] else "Astrology"
                lines.append(f"Source {source_count} [ {data['link']} ]")

    else:
        lines.append(f"Horoscope for {sign_en.capitalize()} is not available at the moment.")
        lines.append("")

    lines.append("")
    lines.append("🌐 _powered by web-search_")

    return "\n".join(lines)


async def format_all_horoscopes_hindi(search_results: List[Dict], detected_lang: str) -> str:
    """Format horoscope for all zodiac signs in Hindi using LLM to extract comprehensive data."""

    # Date header
    current_date = datetime.now().strftime("%d %B %Y")
    # Convert to Hindi month
    month_map = {
        "January": "जनवरी", "February": "फरवरी", "March": "मार्च",
        "April": "अप्रैल", "May": "मई", "June": "जून",
        "July": "जुलाई", "August": "अगस्त", "September": "सितंबर",
        "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
    }
    for eng, hin in month_map.items():
        current_date = current_date.replace(eng, hin)

    # Combine all search results into context
    context = ""
    for i, result in enumerate(search_results[:10], 1):
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        context += f"Result {i}:\nTitle: {title}\nContent: {snippet}\n\n"

    # Use LLM to extract horoscope for ALL 12 signs
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert astrologer helping to extract and format horoscope predictions."),
        ("user", """Based on the following web search results about today's horoscope, extract or generate brief predictions for ALL 12 zodiac signs in Hindi.

Web Search Results:
{context}

Instructions:
1. Extract horoscope predictions for ALL 12 zodiac signs: मेष, वृषभ, मिथुन, कर्क, सिंह, कन्या, तुला, वृश्चिक, धनु, मकर, कुंभ, मीन
2. If a sign is not mentioned in the results, create a brief general positive prediction based on astrological principles
3. Each prediction should be 1-2 sentences about career, health, relationships, or luck
4. Format in Hindi narrative style
5. Keep predictions brief and positive

Return ONLY a JSON object with this structure:
{{
  "मेष": "prediction text in Hindi",
  "वृषभ": "prediction text in Hindi",
  "मिथुन": "prediction text in Hindi",
  "कर्क": "prediction text in Hindi",
  "सिंह": "prediction text in Hindi",
  "कन्या": "prediction text in Hindi",
  "तुला": "prediction text in Hindi",
  "वृश्चिक": "prediction text in Hindi",
  "धनु": "prediction text in Hindi",
  "मकर": "prediction text in Hindi",
  "कुंभ": "prediction text in Hindi",
  "मीन": "prediction text in Hindi"
}}

Return ONLY the JSON, no other text.""")
    ])

    try:
        chain = prompt | llm
        result = await chain.ainvoke({"context": context})

        # Parse JSON response
        import json
        predictions_json = result.content.strip()
        # Remove markdown code blocks if present
        if predictions_json.startswith("```"):
            predictions_json = re.sub(r'^```(?:json)?\n?', '', predictions_json)
            predictions_json = re.sub(r'\n?```$', '', predictions_json)

        predictions = json.loads(predictions_json)

        # Build formatted response
        lines = []
        lines.append(f"🔮 *आज का राशिफल - सभी राशियां ({current_date})*")
        lines.append("")

        # Add predictions for all signs
        for sign_en, sign_hi in ZODIAC_SIGNS_EN_TO_HI.items():
            prediction = predictions.get(sign_hi, "आज आपका दिन शुभ रहेगा।")
            lines.append(f"*{sign_hi} ({sign_en.capitalize()}):*")
            lines.append(f"{prediction}")
            lines.append("")

        # Add instruction to get detailed horoscope
        lines.append("*विस्तृत राशिफल के लिए:*")
        lines.append("अपनी राशि का नाम बताएं, जैसे: \"मेष राशिफल\" या \"Aries horoscope\"")
        lines.append("")

        # Sources
        lines.append("*स्रोत:*")
        unique_links = []
        for result in search_results[:2]:
            link = result.get("link", "")
            if link and link not in unique_links:
                unique_links.append(link)
                source_name = "आज तक" if "aajtak" in link else "नवभारत टाइम्स" if "navbharat" in link else "ज्योतिष"
                lines.append(f"• {source_name}: {link}")

        lines.append("")
        lines.append("🌐 _powered by web-search_")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"LLM extraction failed: {e}, falling back to basic format")
        # Fallback to basic format
        lines = []
        lines.append(f"🔮 *आज का राशिफल - सभी राशियां ({current_date})*")
        lines.append("")

        for sign_en, sign_hi in ZODIAC_SIGNS_EN_TO_HI.items():
            # Find results mentioning this sign
            sign_results = []
            for result in search_results:
                text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
                if sign_en in text or sign_hi in text:
                    sign_results.append(result)

            if sign_results:
                first_result = sign_results[0]
                snippet = first_result.get("snippet", "").strip()
                if snippet:
                    sentences = re.split(r'[।\.]', snippet)
                    brief = sentences[0].strip() if sentences else snippet[:150]
                    lines.append(f"*{sign_hi} ({sign_en.capitalize()}):*")
                    lines.append(f"{brief}...")
                    lines.append("")
            else:
                # Add default positive message if no data found
                lines.append(f"*{sign_hi} ({sign_en.capitalize()}):*")
                lines.append("आज आपका दिन शुभ रहेगा। विस्तृत जानकारी के लिए अपनी राशि का नाम बताएं।")
                lines.append("")

        lines.append("*विस्तृत राशिफल के लिए:*")
        lines.append("अपनी राशि का नाम बताएं, जैसे: \"मेष राशिफल\"")
        lines.append("")
        lines.append("🌐 _powered by web-search_")

        return "\n".join(lines)


async def format_all_horoscopes_english(search_results: List[Dict]) -> str:
    """Format horoscope for all zodiac signs in English using LLM to extract comprehensive data."""

    # Date header
    current_date = datetime.now().strftime("%d %B %Y")

    # Combine all search results into context
    context = ""
    for i, result in enumerate(search_results[:10], 1):
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        context += f"Result {i}:\nTitle: {title}\nContent: {snippet}\n\n"

    # Use LLM to extract horoscope for ALL 12 signs
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert astrologer helping to extract and format horoscope predictions."),
        ("user", """Based on the following web search results about today's horoscope, extract or generate brief predictions for ALL 12 zodiac signs in English.

Web Search Results:
{context}

Instructions:
1. Extract horoscope predictions for ALL 12 zodiac signs: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces
2. If a sign is not mentioned in the results, create a brief general positive prediction based on astrological principles
3. Each prediction should be 1-2 sentences about career, health, relationships, or luck
4. Keep predictions brief and positive

Return ONLY a JSON object with this structure:
{{
  "aries": "prediction text",
  "taurus": "prediction text",
  "gemini": "prediction text",
  "cancer": "prediction text",
  "leo": "prediction text",
  "virgo": "prediction text",
  "libra": "prediction text",
  "scorpio": "prediction text",
  "sagittarius": "prediction text",
  "capricorn": "prediction text",
  "aquarius": "prediction text",
  "pisces": "prediction text"
}}

Return ONLY the JSON, no other text.""")
    ])

    try:
        chain = prompt | llm
        result = await chain.ainvoke({"context": context})

        # Parse JSON response
        import json
        predictions_json = result.content.strip()
        # Remove markdown code blocks if present
        if predictions_json.startswith("```"):
            predictions_json = re.sub(r'^```(?:json)?\n?', '', predictions_json)
            predictions_json = re.sub(r'\n?```$', '', predictions_json)

        predictions = json.loads(predictions_json)

        # Build formatted response
        lines = []
        lines.append(f"🔮 *Today's Horoscope - All Zodiac Signs ({current_date})*")
        lines.append("")

        # Add predictions for all signs
        for sign_en, sign_hi in ZODIAC_SIGNS_EN_TO_HI.items():
            prediction = predictions.get(sign_en, "Today will be a good day for you.")
            lines.append(f"*{sign_en.capitalize()} ({sign_hi}):*")
            lines.append(f"{prediction}")
            lines.append("")

        # Add instruction to get detailed horoscope
        lines.append("*For detailed horoscope:*")
        lines.append("Mention your zodiac sign, e.g.: \"Aries horoscope\" or \"मेष राशिफल\"")
        lines.append("")

        # Sources
        lines.append("*Sources:*")
        unique_links = []
        for result in search_results[:2]:
            link = result.get("link", "")
            if link and link not in unique_links:
                unique_links.append(link)
                source_name = "Aaj Tak" if "aajtak" in link else "Navbharat Times" if "navbharat" in link else "Astrology"
                lines.append(f"• {source_name}: {link}")

        lines.append("")
        lines.append("🌐 _powered by web-search_")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"LLM extraction failed: {e}, falling back to basic format")
        # Fallback to basic format
        lines = []
        lines.append(f"🔮 *Today's Horoscope - All Zodiac Signs ({current_date})*")
        lines.append("")

        for sign_en, sign_hi in ZODIAC_SIGNS_EN_TO_HI.items():
            # Find results mentioning this sign
            sign_results = []
            for result in search_results:
                text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
                if sign_en in text or sign_hi in text:
                    sign_results.append(result)

            if sign_results:
                first_result = sign_results[0]
                snippet = first_result.get("snippet", "").strip()
                if snippet:
                    sentences = re.split(r'[\.]', snippet)
                    brief = sentences[0].strip() if sentences else snippet[:150]
                    lines.append(f"*{sign_en.capitalize()} ({sign_hi}):*")
                    lines.append(f"{brief}...")
                    lines.append("")
            else:
                # Add default positive message if no data found
                lines.append(f"*{sign_en.capitalize()} ({sign_hi}):*")
                lines.append("Today will be a good day. Mention your sign for detailed horoscope.")
                lines.append("")

        lines.append("*For detailed horoscope:*")
        lines.append("Mention your zodiac sign, e.g.: \"Aries horoscope\"")
        lines.append("")
        lines.append("🌐 _powered by web-search_")

        return "\n".join(lines)


async def translate_response(text: str, lang_code: str) -> str:
    """
    Translate response text to the specified language using LLM.

    Args:
        text: Text to translate
        lang_code: Target language code

    Returns:
        Translated text, or original if translation fails
    """
    # Skip if already Hindi or English
    if lang_code in ["en", "hi"] or lang_code not in LANGUAGE_NAMES:
        return text

    try:
        lang_info = LANGUAGE_NAMES.get(lang_code, {})
        language_name = lang_info.get("en", "English")

        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a translator. Translate the following horoscope information to {language_name} ({language_code}).

Keep the formatting with bullets and asterisks (*) intact.
Use the appropriate script for the language (e.g., Kannada script for Kannada, Tamil script for Tamil).
Keep zodiac sign names, URLs in original format (readable for the target language).
Make the translation natural and fluent for astrological content.

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


async def handle_horoscope(state: BotState) -> dict:
    """
    Handle horoscope (rashifal) queries by fetching real-time data from the internet.

    Supports:
    - All 12 zodiac signs (English and Hindi names)
    - Multi-language responses (Hindi/English/regional)
    - Real-time updated predictions from popular astrology websites
    - Professional life, love life, lucky details sections
    - Source links
    """
    entities = state.get("extracted_entities", {})
    sign = entities.get("astro_sign", "").strip()
    detected_lang = state.get("detected_language", "en")

    # Try to extract sign from current query if not in entities
    if not sign:
        current_query = state.get("current_query", "").strip()
        for eng_sign in ZODIAC_SIGNS_EN_TO_HI.keys():
            if eng_sign in current_query.lower():
                sign = eng_sign
                break
        for hi_sign in ZODIAC_SIGNS_HI_TO_EN.keys():
            if hi_sign in current_query:
                sign = hi_sign
                break

    if not sign:
        # User wants ALL horoscopes for today
        logger.info("Fetching horoscope for all zodiac signs")

        # Check if user explicitly wants English
        query_lower = state.get("current_query", "").lower()
        force_english = any(kw in query_lower for kw in ["in english", "english mein", "english me"])

        # Fetch horoscope for all signs
        try:
            # Build search query for all signs
            current_date_str = datetime.now().strftime("%d-%B-%Y").lower()
            search_query = (
                f"all zodiac signs horoscope today {current_date_str} rashifal sabhi rashi "
                f"site:aajtak.in OR site:navbharattimes.indiatimes.com OR site:astrosage.com"
            )

            result = await search_google(query=search_query, max_results=15, country="in", locale="en")

            if not result["success"] or not (result.get("data") or {}).get("results", []):
                # Fallback: show list of signs
                if detected_lang == "hi":
                    signs_list = ", ".join(ZODIAC_SIGNS_EN_TO_HI.values())
                    return {
                        "response_text": f"🔮 *राशिफल*\n\nकृपया अपनी राशि बताएं।\n\n*उपलब्ध राशियां:*\n{signs_list}\n\n*उदाहरण:*\n• \"मेष राशिफल\"\n• \"सिंह आज का राशिफल\"\n• \"धनु राशिफल आज का\"",
                        "response_type": "text",
                        "should_fallback": False,
                        "intent": INTENT,
                    }
                else:
                    signs_list = ", ".join([s.capitalize() for s in ZODIAC_SIGNS_EN_TO_HI.keys()])
                    return {
                        "response_text": f"🔮 *Horoscope*\n\nPlease specify your zodiac sign.\n\n*Available signs:*\n{signs_list}\n\n*Examples:*\n• \"Aries horoscope\"\n• \"Leo horoscope today\"\n• \"Sagittarius daily horoscope\"",
                        "response_type": "text",
                        "should_fallback": False,
                        "intent": INTENT,
                    }

            search_results = (result.get("data") or {}).get("results", [])

            # Format all signs horoscope
            if force_english:
                response_text = await format_all_horoscopes_english(search_results)
            else:
                response_text = await format_all_horoscopes_hindi(search_results, detected_lang)

            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        except Exception as e:
            logger.error(f"All horoscopes fetch error: {e}")
            # Fallback: show list of signs
            if detected_lang == "hi":
                signs_list = ", ".join(ZODIAC_SIGNS_EN_TO_HI.values())
                return {
                    "response_text": f"🔮 *राशिफल*\n\nकृपया अपनी राशि बताएं।\n\n*उपलब्ध राशियां:*\n{signs_list}",
                    "response_type": "text",
                    "should_fallback": False,
                    "intent": INTENT,
                }
            else:
                signs_list = ", ".join([s.capitalize() for s in ZODIAC_SIGNS_EN_TO_HI.keys()])
                return {
                    "response_text": f"🔮 *Horoscope*\n\nPlease specify your zodiac sign.\n\n*Available signs:*\n{signs_list}",
                    "response_type": "text",
                    "should_fallback": False,
                    "intent": INTENT,
                }

    try:
        # Normalize sign
        sign_en = _normalize_sign(sign)
        if not sign_en:
            return {
                "response_text": f"राशि '{sign}' मान्य नहीं है। कृपया सही राशि का नाम बताएं।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        sign_hi = ZODIAC_SIGNS_EN_TO_HI[sign_en]

        # Check if user explicitly wants English
        query_lower = state.get("current_query", "").lower()
        force_english = any(kw in query_lower for kw in ["in english", "english mein", "english me"])

        logger.info(f"Fetching horoscope for {sign_en} ({sign_hi})")

        # Build search query for horoscope
        current_date_str = datetime.now().strftime("%d-%B-%Y").lower()
        search_query = (
            f"{sign_en} horoscope today {current_date_str} rashifal aaj ka "
            f"site:aajtak.in OR site:navbharattimes.indiatimes.com OR site:astrosage.com"
        )

        # Fetch real-time data from web
        result = await search_google(query=search_query, max_results=10, country="in", locale="en")

        if not result["success"]:
            error_msg = sanitize_error(result.get("error", ""), "search")
            return {
                "tool_result": result,
                "response_text": error_msg or "राशिफल अभी प्राप्त नहीं हो सका। कृपया बाद में प्रयास करें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        # Extract search results
        search_results = (result.get("data") or {}).get("results", [])

        if not search_results:
            return {
                "response_text": "कोई राशिफल की जानकारी नहीं मिली। कृपया कुछ देर बाद प्रयास करें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        # Format results
        if force_english:
            response_text = format_horoscope_english(sign_en, search_results)
            target_lang = "en"
        else:
            # Default to Hindi for Indian horoscopes
            response_text = format_horoscope_hindi(sign_hi, sign_en, search_results)
            target_lang = detected_lang if detected_lang != "en" else "hi"

        # Translate to target language if not Hindi or English
        if target_lang not in ["hi", "en"] and not force_english:
            logger.info(f"Translating horoscope to {target_lang}")
            response_text = await translate_response(response_text, target_lang)

        return {
            "tool_result": result,
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Horoscope handler error: {e}", exc_info=True)
        return {
            "response_text": "राशिफल अभी प्राप्त नहीं हो सका। Could not fetch horoscope right now.",
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
