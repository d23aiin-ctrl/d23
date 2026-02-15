"""Extract structured entities from user messages using regex patterns."""

import re
from typing import Any

# Zodiac sign mappings (English + Hindi)
ZODIAC_MAP: dict[str, str] = {
    # English
    "aries": "aries", "taurus": "taurus", "gemini": "gemini", "cancer": "cancer",
    "leo": "leo", "virgo": "virgo", "libra": "libra", "scorpio": "scorpio",
    "sagittarius": "sagittarius", "capricorn": "capricorn", "aquarius": "aquarius", "pisces": "pisces",
    # Hindi
    "मेष": "aries", "mesh": "aries",
    "वृषभ": "taurus", "vrishabh": "taurus",
    "मिथुन": "gemini", "mithun": "gemini",
    "कर्क": "cancer", "kark": "cancer",
    "सिंह": "leo", "singh": "leo", "simha": "leo",
    "कन्या": "virgo", "kanya": "virgo",
    "तुला": "libra", "tula": "libra",
    "वृश्चिक": "scorpio", "vrishchik": "scorpio",
    "धनु": "sagittarius", "dhanu": "sagittarius",
    "मकर": "capricorn", "makar": "capricorn",
    "कुम्भ": "aquarius", "kumbh": "aquarius",
    "मीन": "pisces", "meen": "pisces",
}

# Common Indian city names for weather/fuel/gold queries
COMMON_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Bengaluru", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Bhopal", "Patna", "Vadodara", "Goa", "Chandigarh", "Surat", "Coimbatore",
    "Kochi", "Vizag", "Visakhapatnam", "Noida", "Gurgaon", "Gurugram",
    "Thiruvananthapuram", "Agra", "Varanasi", "Amritsar", "Ranchi",
    "Bhubaneswar", "Dehradun", "Shimla", "Srinagar", "Jammu",
]

# Station code patterns
STATION_CODES = {
    "NDLS": "New Delhi", "HWH": "Howrah", "CSTM": "Mumbai CST", "BCT": "Mumbai Central",
    "SBC": "Bangalore", "MAS": "Chennai", "SC": "Secunderabad", "JP": "Jaipur",
    "LKO": "Lucknow", "PNBE": "Patna", "CDG": "Chandigarh", "ADI": "Ahmedabad",
    "BPL": "Bhopal", "GWL": "Gwalior", "AGC": "Agra Cantt",
}

# Common stock symbols
STOCK_SYMBOLS = {
    "tcs": "TCS", "reliance": "RELIANCE", "infosys": "INFY", "infy": "INFY",
    "hdfc": "HDFCBANK", "hdfcbank": "HDFCBANK", "icici": "ICICIBANK",
    "icicibank": "ICICIBANK", "sbi": "SBIN", "sbin": "SBIN",
    "wipro": "WIPRO", "hcl": "HCLTECH", "hcltech": "HCLTECH",
    "tatamotors": "TATAMOTORS", "tata motors": "TATAMOTORS",
    "tatasteel": "TATASTEEL", "tata steel": "TATASTEEL",
    "bajaj": "BAJFINANCE", "maruti": "MARUTI", "airtel": "BHARTIARTL",
    "bharti": "BHARTIARTL", "itc": "ITC", "lt": "LT",
    "kotak": "KOTAKBANK", "asian paints": "ASIANPAINT", "sunpharma": "SUNPHARMA",
    "nifty": "NIFTY", "sensex": "SENSEX",
}

# Currency code patterns
CURRENCY_MAP = {
    "dollar": "USD", "usd": "USD", "us dollar": "USD",
    "euro": "EUR", "eur": "EUR",
    "pound": "GBP", "gbp": "GBP", "british pound": "GBP",
    "yen": "JPY", "jpy": "JPY", "japanese yen": "JPY",
    "rupee": "INR", "inr": "INR", "rupees": "INR",
    "dirham": "AED", "aed": "AED",
    "riyal": "SAR", "sar": "SAR",
    "canadian dollar": "CAD", "cad": "CAD",
    "australian dollar": "AUD", "aud": "AUD",
    "sgd": "SGD", "singapore dollar": "SGD",
}


def extract_entities(message: str, intent: str) -> dict[str, Any]:
    """Extract entities from a user message based on the classified intent."""
    msg = message.strip()
    entities: dict[str, Any] = {}

    extractors = {
        "pnr_status": _extract_pnr,
        "train_schedule": _extract_train,
        "train_status": _extract_train,
        "train_search": _extract_train_search,
        "horoscope": _extract_zodiac,
        "kundli": _extract_kundli,
        "kundli_match": _extract_kundli,
        "panchang": _extract_panchang,
        "emi_calculate": _extract_emi,
        "sip_calculate": _extract_sip,
        "stock_price": _extract_stock,
        "pmkisan": _extract_pmkisan,
        "driving_license": _extract_dl,
        "vehicle_info": _extract_vehicle,
        "echallan": _extract_echallan,
        "weather": _extract_city,
        "gold_price": _extract_city,
        "fuel_price": _extract_city,
        "currency": _extract_currency,
        "pincode": _extract_pincode,
        "ifsc": _extract_ifsc,
        "holidays": _extract_holidays,
    }

    extractor = extractors.get(intent)
    if extractor:
        entities = extractor(msg)

    return entities


def _extract_pnr(msg: str) -> dict:
    match = re.search(r"\b(\d{10})\b", msg)
    return {"pnr_number": match.group(1)} if match else {}


def _extract_train(msg: str) -> dict:
    match = re.search(r"\b(\d{4,5})\b", msg)
    entities: dict = {}
    if match:
        entities["train_number"] = match.group(1)
    date_match = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", msg)
    if date_match:
        entities["date"] = date_match.group(1).replace("/", "-")
    return entities


def _extract_train_search(msg: str) -> dict:
    entities: dict = {}
    msg_lower = msg.lower()

    # Try station codes first
    codes = re.findall(r"\b([A-Z]{2,4})\b", msg)
    valid_codes = [c for c in codes if c in STATION_CODES]

    if len(valid_codes) >= 2:
        entities["from_station"] = valid_codes[0]
        entities["to_station"] = valid_codes[1]
    else:
        # Try "from X to Y" pattern
        match = re.search(r"from\s+(\w+)\s+to\s+(\w+)", msg_lower)
        if match:
            entities["from_station"] = match.group(1).upper()
            entities["to_station"] = match.group(2).upper()
        else:
            # Try "X to Y" pattern
            match = re.search(r"(\w+)\s+to\s+(\w+)", msg_lower)
            if match:
                entities["from_station"] = match.group(1).upper()
                entities["to_station"] = match.group(2).upper()

    date_match = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", msg)
    if date_match:
        entities["date"] = date_match.group(1).replace("/", "-")

    return entities


def _extract_zodiac(msg: str) -> dict:
    msg_lower = msg.lower()
    for key, sign in ZODIAC_MAP.items():
        if key in msg_lower or key in msg:
            return {"sign": sign}
    return {}


def _extract_kundli(msg: str) -> dict:
    entities: dict = {}
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", msg)
    if date_match:
        entities["date"] = date_match.group(1)
    time_match = re.search(r"(\d{1,2}:\d{2})", msg)
    if time_match:
        entities["time"] = time_match.group(1)
    return entities


def _extract_panchang(msg: str) -> dict:
    entities: dict = {}
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", msg)
    if date_match:
        entities["date"] = date_match.group(1)
    city = _find_city(msg)
    if city:
        entities["city"] = city
    return entities


def _extract_emi(msg: str) -> dict:
    entities: dict = {}

    # Extract amount (with lakh/crore support)
    amount_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)\b", msg, re.IGNORECASE,
    )
    if amount_match:
        entities["principal"] = float(amount_match.group(1)) * 100000
    else:
        crore_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:crore|cr)\b", msg, re.IGNORECASE,
        )
        if crore_match:
            entities["principal"] = float(crore_match.group(1)) * 10000000
        else:
            plain_match = re.search(r"(?:rs\.?|₹|inr)?\s*(\d{4,})", msg, re.IGNORECASE)
            if plain_match:
                entities["principal"] = float(plain_match.group(1))

    # Extract interest rate
    rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", msg)
    if rate_match:
        entities["annual_rate"] = float(rate_match.group(1))

    # Extract tenure
    years_match = re.search(r"(\d+)\s*(?:year|yr|years|yrs)\b", msg, re.IGNORECASE)
    if years_match:
        entities["tenure_months"] = int(years_match.group(1)) * 12
    else:
        months_match = re.search(r"(\d+)\s*(?:month|months|mo)\b", msg, re.IGNORECASE)
        if months_match:
            entities["tenure_months"] = int(months_match.group(1))

    # Extract loan type
    msg_lower = msg.lower()
    if "home" in msg_lower or "housing" in msg_lower or "ghar" in msg_lower:
        entities["loan_type"] = "home"
    elif "car" in msg_lower or "auto" in msg_lower or "vehicle" in msg_lower:
        entities["loan_type"] = "car"
    elif "education" in msg_lower or "student" in msg_lower:
        entities["loan_type"] = "education"
    else:
        entities["loan_type"] = "personal"

    return entities


def _extract_sip(msg: str) -> dict:
    entities: dict = {}

    # Monthly amount
    amount_match = re.search(r"(\d+(?:,\d+)*)\s*(?:/\s*month|per\s*month|monthly|pm)\b", msg, re.IGNORECASE)
    if amount_match:
        entities["monthly_investment"] = float(amount_match.group(1).replace(",", ""))
    else:
        plain_match = re.search(r"(?:rs\.?|₹|inr)?\s*(\d{3,})", msg, re.IGNORECASE)
        if plain_match:
            entities["monthly_investment"] = float(plain_match.group(1))

    # Duration
    years_match = re.search(r"(\d+)\s*(?:year|yr|years|yrs)\b", msg, re.IGNORECASE)
    if years_match:
        entities["duration_years"] = int(years_match.group(1))

    # Return rate
    rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", msg)
    if rate_match:
        entities["expected_return_rate"] = float(rate_match.group(1))
    else:
        entities["expected_return_rate"] = 12.0  # Default assumption

    return entities


def _extract_stock(msg: str) -> dict:
    msg_lower = msg.lower()
    for key, symbol in STOCK_SYMBOLS.items():
        if key in msg_lower:
            return {"symbol": symbol}
    # Try to extract a stock symbol (uppercase letters)
    match = re.search(r"\b([A-Z]{2,15})\b", msg)
    if match and match.group(1) not in {"PNR", "DL", "RC", "EMI", "SIP", "USD", "INR", "IFSC"}:
        return {"symbol": match.group(1)}
    return {}


def _extract_pmkisan(msg: str) -> dict:
    # 10-digit mobile
    mobile_match = re.search(r"\b(\d{10})\b", msg)
    if mobile_match:
        return {"mobile": mobile_match.group(1)}
    # 12-digit aadhaar
    aadhaar_match = re.search(r"\b(\d{12})\b", msg)
    if aadhaar_match:
        return {"aadhaar": aadhaar_match.group(1)}
    return {}


def _extract_dl(msg: str) -> dict:
    match = re.search(r"\b([A-Z]{2}\d{13})\b", msg)
    if match:
        return {"dl_number": match.group(1)}
    # More relaxed: 2 letters followed by digits
    match = re.search(r"\b([A-Z]{2}\d{7,})\b", msg)
    if match:
        return {"dl_number": match.group(1)}
    return {}


def _extract_vehicle(msg: str) -> dict:
    match = re.search(r"\b([A-Z]{2}\d{2}[A-Z]{1,2}\d{4})\b", msg.upper())
    if match:
        return {"vehicle_number": match.group(1)}
    return {}


def _extract_echallan(msg: str) -> dict:
    # Vehicle number
    vehicle_match = re.search(r"\b([A-Z]{2}\d{2}[A-Z]{1,2}\d{4})\b", msg.upper())
    if vehicle_match:
        return {"vehicle_number": vehicle_match.group(1)}
    # 10-digit number (could be mobile or challan)
    num_match = re.search(r"\b(\d{10})\b", msg)
    if num_match:
        return {"vehicle_number": num_match.group(1)}
    return {}


def _extract_city(msg: str) -> dict:
    city = _find_city(msg)
    return {"city": city} if city else {}


def _find_city(msg: str) -> str | None:
    msg_lower = msg.lower()
    for city in COMMON_CITIES:
        if city.lower() in msg_lower:
            return city
    # Try to extract city from "in <city>" or "of <city>" patterns
    match = re.search(r"(?:in|of|for|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", msg)
    if match:
        return match.group(1)
    return None


def _extract_currency(msg: str) -> dict:
    entities: dict = {}
    msg_lower = msg.lower()

    # Extract amount
    amount_match = re.search(r"(\d+(?:\.\d+)?)", msg)

    found_currencies = []
    for key, code in CURRENCY_MAP.items():
        if key in msg_lower:
            if code not in found_currencies:
                found_currencies.append(code)

    if len(found_currencies) >= 2:
        entities["base"] = found_currencies[0]
        entities["quote"] = found_currencies[1]
    elif len(found_currencies) == 1:
        if found_currencies[0] == "INR":
            entities["base"] = "USD"
            entities["quote"] = "INR"
        else:
            entities["base"] = found_currencies[0]
            entities["quote"] = "INR"
    else:
        entities["base"] = "USD"
        entities["quote"] = "INR"

    if amount_match:
        entities["amount"] = float(amount_match.group(1))

    return entities


def _extract_pincode(msg: str) -> dict:
    match = re.search(r"\b(\d{6})\b", msg)
    return {"pincode": match.group(1)} if match else {}


def _extract_ifsc(msg: str) -> dict:
    match = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", msg.upper())
    return {"ifsc": match.group(1)} if match else {}


def _extract_holidays(msg: str) -> dict:
    entities: dict = {}
    year_match = re.search(r"\b(20\d{2})\b", msg)
    if year_match:
        entities["year"] = int(year_match.group(1))
    return entities
