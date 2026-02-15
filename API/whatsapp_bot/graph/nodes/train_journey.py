"""
Train Journey Planner Node

Fetches train options between two cities on a given date using web search.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple

import httpx
from langchain_openai import ChatOpenAI

from whatsapp_bot.state import BotState
from whatsapp_bot.config import settings
from common.tools.serper_search import search_google

try:
    from common.services.ai_language_service import ai_translate_response
    AI_TRANSLATE_AVAILABLE = True
except ImportError:
    AI_TRANSLATE_AVAILABLE = False

logger = logging.getLogger(__name__)

INTENT = "train_journey"
ERAIL_CLASS_CODES = [
    "1A", "2A", "3A", "CC", "FC", "SL", "2S", "3E", "GN", "EA", "EC", "EV", "VC", "VS"
]


def _format_city_name(name: str) -> str:
    if not name:
        return ""
    if re.search(r"[a-zA-Z]", name):
        return name.strip().title()
    return name.strip()


def _extract_route(query: str) -> Tuple[str, str]:
    if not query:
        return "", ""
    query_lower = query.lower()
    match = re.search(r"from\s+(.+?)\s+to\s+(.+?)(?:\s+on|\s*$)", query_lower)
    if match:
        return _format_city_name(match.group(1)), _format_city_name(match.group(2))
    match = re.search(r"(.+?)\s+se\s+(.+?)(?:\s+t(?:ak|k)|\s+ke\s+liye|$)", query_lower)
    if match:
        return _format_city_name(match.group(1)), _format_city_name(match.group(2))

    # Hindi script pattern (e.g., "दिल्ली से बेंगलुरु")
    match = re.search(r"(.+?)\s+से\s+(.+?)(?:\s+तक|\s+के लिए|$)", query)
    if match:
        return _format_city_name(match.group(1)), _format_city_name(match.group(2))
    return "", ""


def _extract_date(query: str) -> str:
    if not query:
        return ""
    match = re.search(r"\b(\d{1,2}\s+[a-zA-Z]+)\b", query)
    if match:
        return match.group(1)
    hindi_months = {
        "जनवरी": "January",
        "फरवरी": "February",
        "मार्च": "March",
        "अप्रैल": "April",
        "मई": "May",
        "जून": "June",
        "जुलाई": "July",
        "अगस्त": "August",
        "सितंबर": "September",
        "सितम्बर": "September",
        "अक्टूबर": "October",
        "नवंबर": "November",
        "नवम्बर": "November",
        "दिसंबर": "December",
        "दिसम्बर": "December",
    }
    match = re.search(r"\b(\d{1,2})\s+(जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|सितम्बर|अक्टूबर|नवंबर|नवम्बर|दिसंबर|दिसम्बर)\b", query)
    if match:
        day = match.group(1)
        month = hindi_months.get(match.group(2), "")
        if month:
            return f"{day} {month}"
    match = re.search(r"\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b", query)
    if match:
        return match.group(1)
    return ""


def _extract_trains(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    trains = []
    for item in results:
        text = " ".join(filter(None, [item.get("title", ""), item.get("snippet", "")])).strip()
        if not text:
            continue
        match = re.search(r"\b(\d{4,5})\b", text)
        if not match:
            continue
        train_no = match.group(1)
        name = text.replace(train_no, "").strip(" -–|:•")
        classes = _extract_classes(text)
        fare = _extract_fare(text)
        trains.append({
            "number": train_no,
            "name": name[:80],
            "classes": classes,
            "fare": fare,
        })
        if len(trains) >= 6:
            break
    return trains


def _extract_classes(text: str) -> str:
    if not text:
        return ""
    tokens = re.findall(r"\b(1A|2A|3A|3E|SL|CC|EC|FC|2S|GN|AC)\b", text.upper())
    seen = []
    for token in tokens:
        if token not in seen:
            seen.append(token)
    return ", ".join(seen)


def _extract_fare(text: str) -> str:
    if not text:
        return ""
    match = re.search(
        r"(₹\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:[-–]|to)\s*₹?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).replace("  ", " ").replace("to", "-")
    match = re.search(r"(₹\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?)", text)
    if match:
        return match.group(1)
    match = re.search(r"\bRs\.?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?", text, flags=re.IGNORECASE)
    if match:
        return match.group(0).replace("Rs.", "₹").replace("Rs", "₹")
    return ""


def _extract_price(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"(₹\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?)", text)
    if match:
        return match.group(1)
    match = re.search(r"\bRs\.?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?", text, flags=re.IGNORECASE)
    if match:
        return match.group(0).replace("Rs.", "₹").replace("Rs", "₹")
    return ""


def _extract_duration(text: str) -> str:
    if not text:
        return ""
    hours_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hours)\b", text, flags=re.IGNORECASE)
    mins_match = re.search(r"(\d{1,2})\s*min", text, flags=re.IGNORECASE)
    hours = hours_match.group(1) if hours_match else ""
    mins = mins_match.group(1) if mins_match else ""
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    if mins:
        return f"{mins}m"
    return ""


def _extract_distance(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"(\d{2,4}(?:\.\d+)?)\s*km", text, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)} km"
    return ""


def _duration_to_hours(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hours)\b", text, flags=re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    match = re.search(r"(\d{1,2})\s*h(?:ours)?\s*(\d{1,2})\s*m", text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1)) + (float(match.group(2)) / 60.0)
    return None


def _extract_fare_amounts(text: str) -> List[int]:
    if not text:
        return []
    amounts = []
    for match in re.findall(r"₹\s*([\d,]+)", text):
        try:
            amounts.append(int(match.replace(",", "")))
        except ValueError:
            continue
    return amounts


def _extract_erail_station_codes(results: List[Dict[str, str]]) -> Tuple[str, str]:
    for item in results:
        link = item.get("link") or ""
        match = re.search(
            r"erail\.in/(?:hi/)?trains-between-stations/[^/]+-([A-Z]{2,5})/[^/]+-([A-Z]{2,5})",
            link,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).upper(), match.group(2).upper()
    return "", ""


def _format_run_days(mask: str) -> str:
    if not mask or len(mask) < 7:
        return ""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    active = [day for idx, day in enumerate(days) if idx < len(mask) and mask[idx] == "1"]
    if len(active) == 7:
        return "Daily"
    return " ".join(active)


def _classes_from_mask(mask: str) -> str:
    if not mask:
        return ""
    trimmed = mask[: len(ERAIL_CLASS_CODES)]
    classes = [
        ERAIL_CLASS_CODES[idx]
        for idx, char in enumerate(trimmed)
        if char == "1" and idx < len(ERAIL_CLASS_CODES)
    ]
    return ", ".join(classes)


def _fare_range_from_erail(fare_str: str, class_mask: str) -> str:
    if not fare_str:
        return ""
    parts = fare_str.split(":")
    if len(parts) < 3:
        return ""
    fares = []
    mask = class_mask or ""
    for idx in range(min(len(ERAIL_CLASS_CODES), len(mask))):
        if mask[idx] != "1":
            continue
        fare_index = idx + 2
        if fare_index >= len(parts):
            continue
        entry = parts[fare_index]
        if not entry:
            continue
        values = entry.split(",")
        if not values or not values[0].isdigit():
            continue
        amount = int(values[0])
        if amount > 0:
            fares.append(amount)
    if not fares:
        return ""
    low = min(fares)
    high = max(fares)
    if low == high:
        return f"₹{low:,}"
    return f"₹{low:,} - ₹{high:,} (approx)"


def _parse_erail_trains(raw: str, limit: int = 6) -> List[Dict[str, str]]:
    if not raw or "^" not in raw:
        return []
    trains = []
    parts = raw.split("^")
    for part in parts[1:]:
        fields = part.split("~")
        if len(fields) < 52:
            continue
        train_no = fields[0].strip()
        if not train_no:
            continue
        train = {
            "number": train_no,
            "name": fields[1].strip(),
            "from_name": fields[6].strip(),
            "to_name": fields[8].strip(),
            "depart": fields[10].strip(),
            "arrive": fields[11].strip(),
            "duration": fields[12].strip(),
            "run_days": fields[13].strip(),
            "classes_mask": fields[21].strip(),
            "train_type": fields[50].strip() or fields[32].strip(),
            "train_id": fields[33].strip(),
            "distance_km": fields[39].strip(),
            "fare_str": fields[41].strip(),
            "note": fields[44].strip(),
            "link": f"https://erail.in/train-enquiry/{train_no}",
        }
        trains.append(train)
        if len(trains) >= limit:
            break
    return trains


def _parse_route_stations(raw: str) -> List[str]:
    if not raw:
        return []
    route_section = raw.split("#^")[-1]
    stations = []
    for part in route_section.split("^"):
        fields = part.split("~")
        if len(fields) < 3:
            continue
        name = fields[2].strip()
        if name:
            stations.append(name)
    return stations


def _summarize_results(results: List[Dict[str, str]], limit: int = 3) -> List[str]:
    lines = []
    for item in results[:limit]:
        title = (item.get("title") or "").strip()
        snippet = (item.get("snippet") or "").strip()
        link = (item.get("link") or "").strip()
        combined = f"{title} {snippet}".strip()
        meta = " | ".join(filter(None, [_extract_price(combined), _extract_duration(combined)]))
        if meta:
            lines.append(f"- {title} ({meta})")
        else:
            lines.append(f"- {title}")
        if link:
            lines.append(f"   • Link: {link}")
    return lines


def _summarize_trains(trains: List[Dict[str, str]], source: str, destination: str, limit: int = 3) -> List[str]:
    lines = []
    for train in trains[:limit]:
        name = train.get("name") or "Train"
        number = train.get("number") or ""
        label = f"{number} - {name}".strip(" -")
        duration = train.get("duration") or ""
        fare = train.get("fare") or _fare_range_from_erail(
            train.get("fare_str") or "",
            train.get("classes_mask") or "",
        )
        parts = [part for part in [duration, fare] if part]
        meta = f" ({' | '.join(parts)})" if parts else ""
        lines.append(f"- {label}{meta}")
        if train.get("depart") and train.get("arrive"):
            lines.append(
                f"   • {train.get('depart')} ({train.get('from_name') or source}) → "
                f"{train.get('arrive')} ({train.get('to_name') or destination})"
            )
        link = train.get("link")
        if link:
            lines.append(f"   • Link: {link}")
    return lines


def _filter_results(results: List[Dict[str, str]], keywords: List[str], domains: List[str]) -> List[Dict[str, str]]:
    filtered = []
    for item in results:
        title = (item.get("title") or "").lower()
        snippet = (item.get("snippet") or "").lower()
        link = (item.get("link") or "").lower()
        if any(dom in link for dom in domains) or any(kw in title or kw in snippet for kw in keywords):
            filtered.append(item)
    return filtered


def _summarize_train_meta(trains: List[Dict[str, str]]) -> Dict[str, str]:
    durations = []
    fares = []
    for train in trains:
        duration_text = train.get("duration") or ""
        duration_val = _duration_to_hours(duration_text)
        if duration_val is not None:
            durations.append(duration_val)
        fare_text = train.get("fare") or _fare_range_from_erail(
            train.get("fare_str") or "",
            train.get("classes_mask") or "",
        )
        fares.extend(_extract_fare_amounts(fare_text))
    duration_range = ""
    if durations:
        low = min(durations)
        high = max(durations)
        duration_range = f"{low:.1f}h - {high:.1f}h (approx)" if low != high else f"{low:.1f}h (approx)"
    fare_range = ""
    if fares:
        low = min(fares)
        high = max(fares)
        fare_range = f"₹{low:,} - ₹{high:,} (approx)" if low != high else f"₹{low:,} (approx)"
    return {"duration": duration_range, "fare": fare_range}


async def _translate_response(text: str, lang: str) -> str:
    if not text or lang == "en" or not AI_TRANSLATE_AVAILABLE:
        return text
    try:
        urls = re.findall(r"https?://\S+", text)
        placeholder_text = text
        for idx, url in enumerate(urls):
            placeholder_text = placeholder_text.replace(url, f"__URL_{idx}__")
        translated = await ai_translate_response(
            text=placeholder_text,
            target_language=lang,
            openai_api_key=settings.openai_api_key,
        )
        for idx, url in enumerate(urls):
            translated = translated.replace(f"__URL_{idx}__", url)
        return translated
    except Exception as e:
        logger.warning(f"AI translation failed for train journey: {e}")
        return text


async def _search_meta(query: str) -> Dict[str, str]:
    result = await search_google(query=query, max_results=6, country="in", locale="en")
    if not result.get("success"):
        return {"price": "", "duration": "", "distance": ""}
    results = (result.get("data") or {}).get("results", []) or []
    return _first_meta_from_results(results)


def _first_meta_from_results(results: List[Dict[str, str]]) -> Dict[str, str]:
    for item in results:
        title = (item.get("title") or "").strip()
        snippet = (item.get("snippet") or "").strip()
        combined = f"{title} {snippet}".strip()
        if not combined:
            continue
        price = _extract_price(combined)
        duration = _extract_duration(combined)
        distance = _extract_distance(combined)
        if price or duration or distance:
            return {"price": price, "duration": duration, "distance": distance}
    return {"price": "", "duration": "", "distance": ""}


async def _format_road_trip_response(
    source: str,
    destination: str,
    date_label: str,
    road_distance: str,
    lang: str = "hi",
) -> str:
    """Use AI to create a road trip itinerary response like Puch AI."""

    prompt = f"""Create a detailed car road trip plan in Hindi for {source} to {destination}. Use polite आप form.

IMPORTANT WHATSAPP FORMATTING:
- Use *bold* with SINGLE asterisk only
- Use • for bullet points
- Do NOT use ### or ** - WhatsApp doesn't support it

GENERATE RESPONSE IN THIS EXACT FORMAT:

[One line intro about this being a long and beautiful journey through different parts of India]

🚗 *मूल जानकारी*
• *दूरी:* लगभग [ACTUAL distance] किमी
• *यात्रा समय:* [hours] घंटे (बिना रुके), लेकिन सुझाई गई यात्रा में [X] रातें शामिल हैं।
• *सबसे अच्छा मार्ग:*
{source} → [City1] → [City2] → [City3] → {destination}

🗓️ *दिन-दर-दिन यात्रा योजना*

*दिन 1: {source} से [मध्य शहर] (लगभग XXX किमी, XX घंटे)*
• सुबह जल्दी निकलें।
• [City] और [City] में रुककर खाना खाएं।
• शाम को [City] पहुंचें।
• *रात्रि विश्राम:* [City] में होटल बुक करें।
• *टिप:* [Local specialty food/attraction to try]

*दिन 2: [City] से [Next City] (लगभग XXX किमी, XX घंटे)*
• सुबह जल्दी निकलें।
• [City] में ब्रेक लें।
• शाम को [City] पहुंचें।
• *रात्रि विश्राम:* [City] में होटल।
• *टिप:* [Local attraction]

*दिन 3: [City] से {destination} (लगभग XXX किमी, XX घंटे)*
• सुबह [City] घूमें।
• दोपहर तक निकल जाएं।
• [City] में ब्रेक लें।
• शाम तक {destination} पहुंच जाएंगे।

✅ *यात्रा के लिए सुझाव*
• *वाहन:* SUV या सेडान (जैसे Creta, City) बेहतर रहेगी।
• *ईंधन:* हर 400-500 किमी पर ईंधन भरवाएं।
• *खाना:* NH पर कई हाईवे ढाबे और फूड जॉइंट्स हैं।
• *दस्तावेज:* लाइसेंस, RC, बीमा, पैन, आधार अवश्य रखें।
• *सुरक्षा:* रात में ड्राइविंग से बचें।

STRICT RULES:
1. Use REAL city names on the actual route between {source} and {destination}
2. Use REALISTIC distances based on actual geography
3. Calculate proper day-wise splits based on 400-600 km per day driving
4. Include actual highway numbers (like NH-44, NH-19) if known
5. Add local tips for each stopover city (famous food, attractions)
6. Use *single asterisk* for bold - NOT double **
7. Do NOT use ### headers
8. Keep it informative like a travel expert"""

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=settings.openai_api_key,
            max_tokens=1500,
        )

        response = llm.invoke([{"role": "user", "content": prompt}])
        return response.content

    except Exception as e:
        logger.error(f"AI road trip formatting failed: {e}")
        # Simple fallback
        return f"""🚗 *{source} से {destination} रोड ट्रिप*

🚗 *मूल जानकारी*
• *दूरी:* लगभग {road_distance or '800-1500'} किमी
• *यात्रा समय:* 2-3 दिन (रुकावटों के साथ)

✅ *सुझाव*
• सुबह जल्दी निकलें
• हर 400-500 किमी पर ईंधन भरवाएं
• रात में ड्राइविंग से बचें
• दस्तावेज साथ रखें

सुरक्षित यात्रा! 🚗"""


async def _format_multimode_response_with_ai(
    source: str,
    destination: str,
    date_label: str,
    trains: List[Dict[str, str]],
    flight_results: List[Dict[str, str]],
    bus_results: List[Dict[str, str]],
    road_results: List[Dict[str, str]],
    flight_meta: Dict[str, str] | None = None,
    bus_meta: Dict[str, str] | None = None,
    lang: str = "hi",
) -> str:
    """Use AI to create a comprehensive travel plan response."""

    # Prepare data for AI
    flight_meta = flight_meta or _first_meta_from_results(flight_results)
    train_meta = _summarize_train_meta(trains)
    bus_meta = bus_meta or _first_meta_from_results(bus_results)

    # Extract road info
    road_snippet = ""
    for item in road_results:
        snippet = item.get("snippet") or ""
        if snippet:
            road_snippet = snippet
            break
    road_distance = _extract_distance(road_snippet)
    road_duration = _extract_duration(road_snippet)

    # Format train data for AI
    train_data = []
    for t in trains[:4]:
        train_info = {
            "number": t.get("number", ""),
            "name": t.get("name", "")[:40],
            "depart": t.get("depart", ""),
            "arrive": t.get("arrive", ""),
            "duration": t.get("duration", ""),
            "classes": t.get("classes") or _classes_from_mask(t.get("classes_mask") or ""),
            "fare": t.get("fare") or _fare_range_from_erail(t.get("fare_str", ""), t.get("classes_mask", "")),
        }
        train_data.append(train_info)

    # Format flight links
    flight_links = [f.get("link", "") for f in flight_results[:2] if f.get("link")]
    bus_links = [b.get("link", "") for b in bus_results[:2] if b.get("link")]

    # Build train info string
    train_info_str = ""
    if train_data:
        train_info_str = ", ".join([
            f"{t['number']} {t['name']} (depart: {t['depart']}, arrive: {t['arrive']}, duration: {t['duration']})"
            for t in train_data
        ])
    else:
        train_info_str = "Multiple trains available"

    prompt = f"""Create a detailed travel plan in Hindi. Use polite आप form, NEVER तुम.

Route: {source} → {destination}
Date: {date_label}

REAL DATA FROM WEB SEARCH:
- Trains: {train_info_str}
- Train fare range: {train_meta.get('fare', '₹300-2500')}
- Train duration: {train_meta.get('duration', '12-18 hours')}
- Flight duration: {flight_meta.get('duration', '1.5-2 hours')}
- Flight fare: {flight_meta.get('price', '₹2,500-6,000')}
- Bus duration: {bus_meta.get('duration', '17-19 hours')}
- Bus fare: {bus_meta.get('price', '₹999-4,599')}
- Road distance: {road_distance or '800-1200 km'}

IMPORTANT WHATSAPP FORMATTING RULES:
- Use *bold* with SINGLE asterisk only (not double **)
- Use • for bullet points
- Use emojis for section headers
- Do NOT use ### or ** markdown - WhatsApp doesn't support it
- Keep lines readable

GENERATE RESPONSE IN THIS EXACT FORMAT:

{date_label} को {source} से {destination} के लिए यात्रा की योजना नीचे दी गई है। आपके पास ट्रेन, बस और हवाई जहाज के विकल्प है:

🚆 *ट्रेन से यात्रा*
{source} जंक्शन से {destination} के लिए कई ट्रेनें उपलब्ध हैं।
• *दूरी:* लगभग [distance] किमी
• *समय:* [hours] घंटे तक
• *तेज़ ट्रेन:* राजधानी एक्सप्रेस ([number]): [time] बजे प्रस्थान
  श्रमजीवी एक्सप्रेस ([number]): [time] बजे प्रस्थान
• ट्रेन टिकट [ https://www.irctc.co.in ]

🚌 *बस से यात्रा*
• *पहली बस:* सुबह 9:00 बजे
• *आखिरी बस:* रात 9:00 बजे
• *औसत समय:* {bus_meta.get('duration', '17-19 घंटे')}
• *किराया:* {bus_meta.get('price', '₹999 से ₹4,599')}
• *बोर्डिंग:* मुख्य बस स्टैंड, {source}
• बस टिकट [ https://www.redbus.in ]

✈️ *हवाई जहाज से यात्रा*
• *समय:* लगभग {flight_meta.get('duration', '1.5-2 घंटे')}
• *किराया:* {flight_meta.get('price', '₹2,500 से ₹6,000')}
• *सुझाव:* कई बार फ्लाइट ट्रेन से भी सस्ती!
• फ्लाइट बुकिंग [ https://www.makemytrip.com ]

✅ *सुझाव:*
• समय कम है → फ्लाइट
• बजट कम है → ट्रेन (स्लीपर/3AC)
• समूह में यात्रा → बस

यात्रा सुरक्षित रहे! 🚆✈️🚌

STRICT RULES:
1. Use train data provided above if available
2. Use *single asterisk* for bold - NOT double **
3. Do NOT use ### headers - use emoji headers instead
4. Keep response concise and WhatsApp-friendly
5. No "powered by" or extra footer text"""

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=settings.openai_api_key,
            max_tokens=1200,
        )

        response = llm.invoke([{"role": "user", "content": prompt}])
        return response.content

    except Exception as e:
        logger.error(f"AI travel formatting failed: {e}")
        # Fallback to simple format
        return _format_multimode_response_simple(
            source, destination, date_label, trains,
            flight_results, bus_results, road_results,
            flight_meta, bus_meta
        )


def _format_multimode_response_simple(
    source: str,
    destination: str,
    date_label: str,
    trains: List[Dict[str, str]],
    flight_results: List[Dict[str, str]],
    bus_results: List[Dict[str, str]],
    road_results: List[Dict[str, str]],
    flight_meta: Dict[str, str] | None = None,
    bus_meta: Dict[str, str] | None = None,
) -> str:
    """Simple fallback format if AI fails."""
    lines = [
        f"🧳 *{source} → {destination}*",
        f"📅 {date_label}",
        "",
    ]

    flight_meta = flight_meta or _first_meta_from_results(flight_results)
    lines.append("✈️ *Flight* (fastest)")
    if flight_meta["duration"] or flight_meta["price"]:
        lines.append(f"   {flight_meta.get('duration', '')} | {flight_meta.get('price', '')}")

    train_meta = _summarize_train_meta(trains)
    lines.append("🚆 *Train* (comfortable)")
    if train_meta["duration"] or train_meta["fare"]:
        lines.append(f"   {train_meta.get('duration', '')} | {train_meta.get('fare', '')}")

    bus_meta = bus_meta or _first_meta_from_results(bus_results)
    lines.append("🚌 *Bus* (budget)")
    if bus_meta["duration"] or bus_meta["price"]:
        lines.append(f"   {bus_meta.get('duration', '')} | {bus_meta.get('price', '')}")

    lines.append("")
    lines.append("_Details: makemytrip.com, irctc.co.in, redbus.in_")

    return "\n".join(lines)


def _format_multimode_response(
    source: str,
    destination: str,
    date_label: str,
    trains: List[Dict[str, str]],
    flight_results: List[Dict[str, str]],
    bus_results: List[Dict[str, str]],
    road_results: List[Dict[str, str]],
    flight_meta: Dict[str, str] | None = None,
    bus_meta: Dict[str, str] | None = None,
) -> str:
    """Sync wrapper for compatibility - returns simple format."""
    return _format_multimode_response_simple(
        source, destination, date_label, trains,
        flight_results, bus_results, road_results,
        flight_meta, bus_meta
    )


async def _fetch_erail_trains(from_code: str, to_code: str) -> str:
    url = (
        "https://erail.in/rail/getTrains.aspx"
        f"?Station_From={from_code}&Station_To={to_code}&DataSource=0&Language=0&Cache=1"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return ""
        return response.text


async def _fetch_erail_route(train_id: str) -> str:
    if not train_id:
        return ""
    url = (
        "https://erail.in/data.aspx"
        f"?Action=TRAINROUTE&Password=2012&Cache=1&Data1={train_id}&Data2=0"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return ""
        return response.text


async def handle_train_journey(state: BotState) -> dict:
    """
    Node function: Fetches train options between two cities on a date.
    """
    entities = state.get("extracted_entities", {}) or {}
    detected_lang = state.get("detected_language", "en")
    query = state.get("current_query", "") or state.get("whatsapp_message", {}).get("text", "")

    source = (entities.get("source_city") or "").strip()
    destination = (entities.get("destination_city") or "").strip()
    journey_date = (entities.get("journey_date") or "").strip()

    if not source or not destination:
        src, dst = _extract_route(query)
        source = source or src
        destination = destination or dst
    if not journey_date:
        journey_date = _extract_date(query)

    if not source or not destination:
        prompt = "Please provide source and destination, e.g., 'train from Bengaluru to Delhi on 26 January'."
        return {
            "response_text": prompt,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    date_label = journey_date or datetime.now().strftime("%d %B")
    search_query = (
        f"trains from {source} to {destination} on {date_label} fare classes "
        "site:erail.in OR site:ixigo.com OR site:goibibo.com OR site:confirmtkt.com OR site:indiarailinfo.com"
    )
    query_lower = query.lower()
    train_only = any(kw in query_lower for kw in ["train", "railway", "rail", "ट्रेन", "रेल", "रेलगाड़ी"])
    has_plan_word = any(kw in query_lower for kw in ["plan", "planning"]) or any(
        kw in query for kw in ["प्लान", "योजना"]
    )
    has_travel_word = any(kw in query_lower for kw in ["travel", "trip", "journey"]) or "यात्रा" in query
    if any(kw in query_lower for kw in ["travel plan", "trip plan", "plan travel", "plan trip", "यात्रा प्लान", "ट्रिप प्लान", "यात्रा योजना"]):
        train_only = False
    if has_plan_word and has_travel_word:
        train_only = False
    if entities.get("multi_mode"):
        train_only = False

    try:
        result = await search_google(query=search_query, max_results=8, country="in", locale="en")
        if not result["success"]:
            return {
                "tool_result": result,
                "response_text": "Could not fetch trains right now. Please try again.",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        data = result.get("data", {}) or {}
        results = data.get("results", [])
        trains = []
        from_code, to_code = _extract_erail_station_codes(results)
        if from_code and to_code:
            try:
                raw = await _fetch_erail_trains(from_code, to_code)
                trains = _parse_erail_trains(raw)
            except Exception as e:
                logger.warning(f"Erail fetch failed: {e}")
        if not trains:
            trains = _extract_trains(results)

        if train_only:
            lines = [
                f"🚆 *Trains from {source} to {destination}*",
                f"🗓️ Date: {date_label}",
                "",
            ]
        else:
            lines = []
        via_added = 0
        if trains and train_only:
            for idx, train in enumerate(trains, start=1):
                name = train.get("name") or "Train"
                number = train.get("number") or ""
                lines.append(f"{idx}. {number} - {name}")
                if train.get("depart"):
                    lines.append(f"   • Depart: {train.get('depart')} ({train.get('from_name') or source})")
                if train.get("arrive"):
                    lines.append(f"   • Arrive: {train.get('arrive')} ({train.get('to_name') or destination})")
                duration = train.get("duration") or ""
                if duration:
                    if "hr" not in duration:
                        duration = f"{duration} hr"
                    lines.append(f"   • Duration: {duration}")
                distance = train.get("distance_km") or ""
                if distance:
                    if "km" not in distance:
                        distance = f"{distance} km"
                    lines.append(f"   • Distance: {distance}")
                run_days = _format_run_days(train.get("run_days") or "")
                if run_days:
                    lines.append(f"   • Runs: {run_days}")
                train_type = train.get("train_type") or ""
                if train_type:
                    lines.append(f"   • Type: {train_type}")
                classes = train.get("classes") or _classes_from_mask(train.get("classes_mask") or "")
                if classes:
                    lines.append(f"   • Classes: {classes}")
                fare = train.get("fare") or _fare_range_from_erail(
                    train.get("fare_str") or "",
                    train.get("classes_mask") or "",
                )
                if fare:
                    lines.append(f"   • Fare: {fare}")
                if train.get("note"):
                    lines.append(f"   • Note: {train.get('note')}")
                if from_code and to_code and idx <= 3 and train.get("train_id"):
                    try:
                        route_raw = await _fetch_erail_route(train["train_id"])
                        stations = _parse_route_stations(route_raw)
                        if len(stations) > 2:
                            via = ", ".join(stations[1:5])
                            lines.append(f"   • Via: {via}")
                            via_added += 1
                    except Exception as e:
                        logger.warning(f"Erail route fetch failed: {e}")
                link = train.get("link")
                if link:
                    lines.append(f"   • Link: {link}")
        elif train_only:
            lines.append("No train details found. Try another date or check IRCTC.")

        if not train_only:
            flight_query = (
                f"flight tickets from {source} to {destination} {date_label} "
                "site:skyscanner.co.in OR site:makemytrip.com OR site:goibibo.com OR site:ixigo.com"
            )
            bus_query = (
                f"bus tickets from {source} to {destination} {date_label} "
                "site:redbus.in OR site:abhibus.com OR site:paytm.com OR site:makemytrip.com"
            )
            road_query = f"distance from {source} to {destination} by road travel time"

            flight_results = []
            bus_results = []
            road_results = []
            try:
                flight_data = await search_google(query=flight_query, max_results=5, country="in", locale="en")
                flight_results = (flight_data.get("data") or {}).get("results", []) if flight_data.get("success") else []
            except Exception as e:
                logger.warning(f"Flight search failed: {e}")
            try:
                bus_data = await search_google(query=bus_query, max_results=5, country="in", locale="en")
                bus_results = (bus_data.get("data") or {}).get("results", []) if bus_data.get("success") else []
            except Exception as e:
                logger.warning(f"Bus search failed: {e}")
            try:
                road_data = await search_google(query=road_query, max_results=3, country="in", locale="en")
                road_results = (road_data.get("data") or {}).get("results", []) if road_data.get("success") else []
            except Exception as e:
                logger.warning(f"Road search failed: {e}")

            flight_results = _filter_results(
                flight_results,
                keywords=["flight", "airfare", "airline", "air ticket", "flights"],
                domains=["makemytrip.com/flights", "goibibo.com/flights", "ixigo.com/cheap-flights", "skyscanner", "cleartrip.com/flights"],
            )
            bus_results = _filter_results(
                bus_results,
                keywords=["bus", "buses", "bus tickets"],
                domains=["redbus.in", "abhibus.com", "paytm.com/bus", "makemytrip.com/bus"],
            )

            flight_meta = _first_meta_from_results(flight_results)
            if not flight_meta["duration"] or not flight_meta["price"]:
                extra_meta = await _search_meta(f"{source} to {destination} flight duration {date_label}")
                flight_meta = {
                    "duration": flight_meta["duration"] or extra_meta.get("duration", ""),
                    "price": flight_meta["price"] or extra_meta.get("price", ""),
                    "distance": flight_meta["distance"] or extra_meta.get("distance", ""),
                }
            if not flight_meta["price"]:
                extra_price = await _search_meta(f"{source} to {destination} flight fare {date_label}")
                flight_meta["price"] = extra_price.get("price", "") or flight_meta["price"]

            bus_meta = _first_meta_from_results(bus_results)
            if not bus_meta["duration"] or not bus_meta["price"]:
                extra_bus = await _search_meta(f"{source} to {destination} bus duration {date_label}")
                bus_meta = {
                    "duration": bus_meta["duration"] or extra_bus.get("duration", ""),
                    "price": bus_meta["price"] or extra_bus.get("price", ""),
                    "distance": bus_meta["distance"] or extra_bus.get("distance", ""),
                }
            if not bus_meta["price"]:
                extra_bus_price = await _search_meta(f"{source} to {destination} bus fare {date_label}")
                bus_meta["price"] = extra_bus_price.get("price", "") or bus_meta["price"]

            # Extract road distance for road trip
            road_snippet = ""
            for item in road_results:
                snippet = item.get("snippet") or ""
                if snippet:
                    road_snippet = snippet
                    break
            road_distance = _extract_distance(road_snippet)

            # Check if this is a road trip query
            is_road_trip = entities.get("road_trip") or any(
                kw in query_lower for kw in ["road trip", "roadtrip", "car trip", "car travel", "by car", "car se", "drive"]
            )

            if is_road_trip:
                # Use road trip specific formatting
                response_text = await _format_road_trip_response(
                    source=source,
                    destination=destination,
                    date_label=date_label,
                    road_distance=road_distance,
                    lang=detected_lang,
                )
                return {
                    "tool_result": result,
                    "response_text": response_text,
                    "response_type": "text",
                    "should_fallback": False,
                    "intent": INTENT,
                }

            # Use AI-enhanced formatting for comprehensive response
            response_text = await _format_multimode_response_with_ai(
                source=source,
                destination=destination,
                date_label=date_label,
                trains=trains,
                flight_results=flight_results,
                bus_results=bus_results,
                road_results=road_results,
                flight_meta=flight_meta,
                bus_meta=bus_meta,
                lang=detected_lang,
            )
            # Skip translation if already in target language from AI
            if detected_lang not in ["hi", "en"]:
                response_text = await _translate_response(response_text, detected_lang)
            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        if results:
            lines.append("")
            lines.append("Sources:")
            for idx, item in enumerate(results[:3], start=1):
                link = item.get("link") or ""
                if link:
                    lines.append(f"{idx}) {link}")
        if from_code and to_code and trains and via_added == 0:
            lines.append("")
            lines.append("Note: Route details are not available right now.")

        response_text = "\n".join(lines)
        response_text = await _translate_response(response_text, detected_lang)

        return {
            "tool_result": result,
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Train journey handler error: {e}")
        return {
            "response_text": "Could not fetch trains right now.",
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
