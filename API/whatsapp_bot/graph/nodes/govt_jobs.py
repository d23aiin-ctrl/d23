"""
Government Jobs Node

Fetches real-time government job listings from the internet for any Indian state or central government.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from whatsapp_bot.state import BotState
from common.tools.serper_search import search_google
from common.utils.response_formatter import sanitize_error
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from whatsapp_bot.config import settings

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

INTENT = "govt_jobs"

STATE_ALIASES = {
    "delhi": "Delhi",
    "bihar": "Bihar",
    "uttar pradesh": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "maharashtra": "Maharashtra",
    "karnataka": "Karnataka",
    "tamil nadu": "Tamil Nadu",
    "tn": "Tamil Nadu",
    "west bengal": "West Bengal",
    "wb": "West Bengal",
    "rajasthan": "Rajasthan",
    "gujarat": "Gujarat",
    "kerala": "Kerala",
    "telangana": "Telangana",
    "andhra pradesh": "Andhra Pradesh",
    "ap": "Andhra Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "mp": "Madhya Pradesh",
    "jharkhand": "Jharkhand",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "haryana": "Haryana",
    "chhattisgarh": "Chhattisgarh",
    "assam": "Assam",
    "jammu": "Jammu & Kashmir",
    "kashmir": "Jammu & Kashmir",
}


def _extract_state(query: str) -> Optional[str]:
    query_lower = query.lower()
    for key, label in STATE_ALIASES.items():
        if re.search(rf"\b{re.escape(key)}\b", query_lower):
            return label
    # Simple "in/for" extraction
    match = re.search(r"(?:in|for)\s+([a-zA-Z\s]+)$", query_lower)
    if match:
        candidate = match.group(1).strip()
        return candidate.title() if candidate else None
    return None




def extract_job_info(result: Dict) -> Dict:
    """Extract job information from search result."""
    title = result.get("title", "").strip()
    snippet = result.get("snippet", "").strip()
    link = result.get("link", "").strip()

    # Extract number of posts if available
    posts_match = re.search(r'(\d+(?:,\d+)*)\s*(?:posts?|vacancies|पद|रिक्तियां)', title + " " + snippet, re.IGNORECASE)
    posts = posts_match.group(1) if posts_match else ""

    # Extract date if available
    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर)\s+\d{4})', title + " " + snippet, re.IGNORECASE)
    date = date_match.group(1) if date_match else ""

    return {
        "title": title,
        "snippet": snippet[:200],  # Limit snippet length
        "link": link,
        "posts": posts,
        "date": date
    }


async def format_jobs_with_ai(search_results: List[Dict], state_name: Optional[str], lang: str = "hi") -> str:
    """Use AI to create a comprehensive, well-structured govt jobs response."""

    # Extract key info from search results
    jobs_data = []
    for result in search_results[:8]:
        job_info = extract_job_info(result)
        if job_info["title"]:
            jobs_data.append({
                "title": job_info["title"],
                "link": job_info["link"],
                "posts": job_info["posts"],
                "date": job_info["date"],
                "snippet": result.get("snippet", "")[:150]
            })

    current_date = datetime.now().strftime("%d %B %Y")

    # Convert to Hindi date
    month_map = {
        "January": "जनवरी", "February": "फरवरी", "March": "मार्च",
        "April": "अप्रैल", "May": "मई", "June": "जून",
        "July": "जुलाई", "August": "अगस्त", "September": "सितंबर",
        "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
    }
    hindi_date = current_date
    for eng, hin in month_map.items():
        hindi_date = hindi_date.replace(eng, hin)

    jobs_json = "\n".join([f"- {j['title']} | Posts: {j['posts'] or 'N/A'} | Date: {j['date'] or 'N/A'} | Link: {j['link']}" for j in jobs_data])

    prompt = f"""आज की तारीख: {hindi_date}
{"राज्य: " + state_name if state_name else "केंद्र सरकार की नौकरियां"}

Search Results:
{jobs_json}

इन search results के आधार पर एक comprehensive सरकारी नौकरी अपडेट बनाएं। Format:

1. **Introduction** (1 line): आज की तारीख और context

2. **◆ नवीनतम सरकारी नौकरियां (2026):**
   - 5 main jobs with:
     • Job name - पद: position (vacancies)
     • अंतिम तिथि: date
     • अधिसूचना देखें [ link ]

3. **◆ लड़कियों के लिए शीर्ष अवसर:**
   - 3-4 bullet points of jobs good for women (from search or general knowledge)
   - One helpful link

4. **◆ तैयारी के लिए सुझाव:**
   - प्रतियोगी परीक्षाएं: list
   - सबसे अधिक वेतन वाली नौकरियां: list
   - नौकरी के लाभ: benefits

5. **◆ कैसे आवेदन करें?**
   - 4 numbered steps
   - Include official website links (ssc.gov.in, upsc.gov.in)

6. **Footer tip** with 1-2 helpful links

IMPORTANT:
- Use polite आप form, not तुम
- Keep links as plain URLs in brackets [ url ]
- Be informative but concise
- Use actual data from search results where available"""

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
        logger.error(f"AI formatting failed: {e}")
        # Fallback to simple format
        return _simple_format_hindi(jobs_data, state_name, hindi_date)


def _simple_format_hindi(jobs_data: List[Dict], state_name: Optional[str], date: str) -> str:
    """Simple fallback format if AI fails."""
    lines = []
    lines.append(f"📋 *सरकारी नौकरी अपडेट्स* ({date})")
    lines.append("")

    for idx, job in enumerate(jobs_data[:5], 1):
        title = re.sub(r'\s*[-–|]\s*(FreeJobAlert|Sarkari|Result).*$', '', job['title'], flags=re.IGNORECASE)
        lines.append(f"{idx}. *{title[:50]}*")
        if job['posts']:
            lines.append(f"   पद: {job['posts']}")
        if job['date']:
            lines.append(f"   अंतिम तिथि: {job['date']}")
        lines.append(f"   🔗 {job['link']}")
        lines.append("")

    lines.append("_और जानकारी के लिए \"more\" टाइप करें_")
    return "\n".join(lines)


async def format_jobs_with_ai_english(search_results: List[Dict], state_name: Optional[str]) -> str:
    """Use AI to create a comprehensive, well-structured English govt jobs response."""

    jobs_data = []
    for result in search_results[:8]:
        job_info = extract_job_info(result)
        if job_info["title"]:
            jobs_data.append({
                "title": job_info["title"],
                "link": job_info["link"],
                "posts": job_info["posts"],
                "date": job_info["date"],
                "snippet": result.get("snippet", "")[:150]
            })

    current_date = datetime.now().strftime("%d %B %Y")
    jobs_json = "\n".join([f"- {j['title']} | Posts: {j['posts'] or 'N/A'} | Date: {j['date'] or 'N/A'} | Link: {j['link']}" for j in jobs_data])

    prompt = f"""Today's date: {current_date}
{"State: " + state_name if state_name else "Central Government Jobs"}

Search Results:
{jobs_json}

Create a comprehensive government job update based on these search results. Format:

1. **Introduction** (1 line): Today's date and context

2. **◆ Latest Government Jobs (2026):**
   - 5 main jobs with:
     • Job name - Position: role (vacancies)
     • Last Date: date
     • View notification [ link ]

3. **◆ Top Opportunities for Women:**
   - 3-4 bullet points of jobs suitable for women
   - One helpful link

4. **◆ Preparation Tips:**
   - Competitive exams: SSC, UPSC, RRB, Banking, etc.
   - Highest paying jobs: IAS, IPS, IFS, etc.
   - Job benefits: security, pension, medical, housing

5. **◆ How to Apply?**
   - 4 numbered steps
   - Include official website links (ssc.gov.in, upsc.gov.in)

6. **Footer tip** with 1-2 helpful links

IMPORTANT:
- Be professional and helpful
- Keep links as plain URLs in brackets [ url ]
- Be informative but concise
- Use actual data from search results where available"""

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
        logger.error(f"AI formatting (English) failed: {e}")
        return _simple_format_english(jobs_data, state_name, current_date)


def _simple_format_english(jobs_data: List[Dict], state_name: Optional[str], date: str) -> str:
    """Simple fallback format if AI fails."""
    lines = []
    lines.append(f"📋 *Govt Job Updates* ({date})")
    lines.append("")

    for idx, job in enumerate(jobs_data[:5], 1):
        title = re.sub(r'\s*[-–|]\s*(FreeJobAlert|Sarkari|Result).*$', '', job['title'], flags=re.IGNORECASE)
        lines.append(f"{idx}. *{title[:50]}*")
        if job['posts']:
            lines.append(f"   Posts: {job['posts']}")
        if job['date']:
            lines.append(f"   Last Date: {job['date']}")
        lines.append(f"   🔗 {job['link']}")
        lines.append("")

    lines.append("_Type \"more\" for more jobs_")
    return "\n".join(lines)


def format_jobs_from_search_english(search_results: List[Dict], state_name=None) -> str:
    """Sync wrapper - not used anymore, kept for compatibility."""
    jobs_data = []
    for result in search_results[:5]:
        job_info = extract_job_info(result)
        if job_info["title"]:
            jobs_data.append(job_info)
    return _simple_format_english(jobs_data, state_name, datetime.now().strftime("%d %B %Y"))


async def translate_response(text: str, lang_code: str) -> str:
    """
    Translate response text to the specified language using LLM.

    Args:
        text: Text to translate
        lang_code: Target language code (e.g., 'kn' for Kannada)

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
            ("system", """You are a translator. Translate the following government job information to {language_name} ({language_code}).

Keep the formatting with bullets and asterisks (*) intact.
Use the appropriate script for the language (e.g., Kannada script for Kannada, Tamil script for Tamil).
Keep job names, URLs, and dates in original format (readable for the target language).
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


def _extract_organization(title: str, snippet: str) -> str:
    """Extract organization name from title or snippet."""
    text = f"{title} {snippet}".lower()

    # Common organizations
    orgs = {
        "ssc": "SSC (Staff Selection Commission)",
        "upsc": "UPSC",
        "railway": "Indian Railways",
        "rrb": "Railway Recruitment Board",
        "bank": "Banking",
        "ibps": "IBPS",
        "sbi": "State Bank of India",
        "rbi": "Reserve Bank of India",
        "army": "Indian Army",
        "navy": "Indian Navy",
        "air force": "Indian Air Force",
        "police": "Police Department",
        "crpf": "CRPF",
        "bsf": "BSF",
        "cisf": "CISF",
        "income tax": "Income Tax Department",
        "customs": "Customs Department",
        "postal": "India Post",
        "aiims": "AIIMS",
        "esic": "ESIC",
        "drdo": "DRDO",
        "isro": "ISRO",
        "ongc": "ONGC",
        "bhel": "BHEL",
        "ntpc": "NTPC",
        "coal india": "Coal India",
        "bpsc": "BPSC",
        "uppsc": "UPPSC",
        "mpsc": "MPSC",
        "kpsc": "KPSC",
        "wbpsc": "WBPSC",
        "tnpsc": "TNPSC",
        "gpsc": "GPSC",
        "rpsc": "RPSC",
    }

    for key, org_name in orgs.items():
        if key in text:
            return org_name

    return ""


def _extract_qualification(snippet: str) -> str:
    """Extract qualification from snippet."""
    text = snippet.lower()

    qualifications = [
        ("ph.d", "Ph.D"),
        ("post graduate", "Post Graduate"),
        ("pg ", "Post Graduate"),
        ("m.tech", "M.Tech"),
        ("mtech", "M.Tech"),
        ("m.sc", "M.Sc"),
        ("msc", "M.Sc"),
        ("mba", "MBA"),
        ("m.a", "M.A"),
        ("graduate", "Graduate"),
        ("b.tech", "B.Tech"),
        ("btech", "B.Tech"),
        ("b.e", "B.E"),
        ("b.sc", "B.Sc"),
        ("bsc", "B.Sc"),
        ("b.a", "B.A"),
        ("b.com", "B.Com"),
        ("12th", "12th Pass"),
        ("10+2", "12th Pass"),
        ("intermediate", "12th Pass"),
        ("10th", "10th Pass"),
        ("matric", "10th Pass"),
        ("8th", "8th Pass"),
        ("iti", "ITI"),
        ("diploma", "Diploma"),
    ]

    for key, qual in qualifications:
        if key in text:
            return qual

    return ""


def _extract_salary(snippet: str) -> str:
    """Extract salary information from snippet."""
    # Look for salary patterns
    salary_match = re.search(
        r'(?:salary|pay|वेतन)[:\s]*(?:rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\s*-\s*\d+(?:,\d+)*)?)',
        snippet,
        re.IGNORECASE
    )
    if salary_match:
        return f"₹{salary_match.group(1)}"

    # Look for pay scale
    pay_match = re.search(
        r'(?:pay\s*(?:scale|band|level)|level)[:\s]*(\d+(?:\s*-\s*\d+)?)',
        snippet,
        re.IGNORECASE
    )
    if pay_match:
        return f"Level {pay_match.group(1)}"

    return ""


def _is_recent_job(date_str: str) -> bool:
    """Check if job posting is recent (within last 7 days or future date)."""
    if not date_str:
        return False

    try:
        # Try to parse date
        current = datetime.now()

        # Check for keywords indicating new/recent
        if any(kw in date_str.lower() for kw in ["today", "new", "latest", "jan 2026", "feb 2026"]):
            return True

        # Try common date formats
        for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d %B %Y", "%d %b %Y"]:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                # If last date is in future, it's a new job
                if parsed >= current:
                    return True
                # If within last 7 days
                if (current - parsed).days <= 7:
                    return True
            except ValueError:
                continue
    except Exception:
        pass

    return False


def _build_search_query_for_state(state_name: Optional[str], current_year: str = "2026") -> str:
    """Build optimized search query for state or central government jobs."""
    if state_name:
        return (
            f"{state_name} government jobs latest vacancy {current_year} notification recruitment "
            f"site:.gov.in OR site:freejobalert.com OR site:sarkariresult.com OR site:employmentnews.gov.in"
        )
    else:
        return (
            f"central government jobs India latest vacancy {current_year} notification recruitment "
            f"SSC UPSC Railway Bank "
            f"site:ssc.nic.in OR site:upsc.gov.in OR site:freejobalert.com OR site:employmentnews.gov.in"
        )


async def handle_govt_jobs(state: BotState) -> dict:
    """
    Handle government jobs queries by fetching real-time data from the internet.

    Supports:
    - All Indian states (Bihar, UP, Maharashtra, etc.)
    - Central government jobs
    - Multi-language responses (Hindi/English/regional)
    - Real-time updated job listings
    """
    user_message = state.get("current_query", "").strip() or state.get("whatsapp_message", {}).get("text", "")
    detected_lang = state.get("detected_language", "en")

    try:
        # Check if user explicitly wants English
        query_lower = user_message.lower()
        force_english = any(kw in query_lower for kw in ["in english", "english mein", "english me"])

        # Detect state from query
        state_name = _extract_state(user_message)

        # Build search query
        search_query = _build_search_query_for_state(state_name)

        logger.info(f"Fetching government jobs for state: {state_name or 'Central'}")
        logger.info(f"Search query: {search_query}")

        # Fetch real-time data from web
        result = await search_google(query=search_query, max_results=12, country="in", locale="en")

        if not result["success"]:
            error_msg = sanitize_error(result.get("error", ""), "search")
            return {
                "tool_result": result,
                "response_text": error_msg or "सरकारी नौकरी की जानकारी अभी प्राप्त नहीं हो सकी। कृपया बाद में प्रयास करें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        # Extract search results
        search_results = (result.get("data") or {}).get("results", [])

        if not search_results:
            return {
                "response_text": "कोई सरकारी नौकरी की जानकारी नहीं मिली। कृपया कुछ देर बाद प्रयास करें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        # Extract structured job data for rich cards
        jobs_structured = []
        for res in search_results[:8]:
            job_info = extract_job_info(res)
            if job_info["title"]:
                # Clean title
                clean_title = re.sub(r'\s*[-–|]\s*(FreeJobAlert|Sarkari|Result|sarkariresult|freejobalert).*$', '', job_info["title"], flags=re.IGNORECASE)
                jobs_structured.append({
                    "title": clean_title.strip()[:80],
                    "organization": _extract_organization(job_info["title"], job_info.get("snippet", "")),
                    "vacancies": job_info["posts"] or "",
                    "last_date": job_info["date"] or "",
                    "qualification": _extract_qualification(job_info.get("snippet", "")),
                    "salary": _extract_salary(job_info.get("snippet", "")),
                    "location": state_name or "All India",
                    "url": job_info["link"],
                    "is_new": _is_recent_job(job_info["date"]),
                    "snippet": job_info.get("snippet", "")[:100]
                })

        # Format results using AI for rich, comprehensive response
        if force_english:
            # Use AI to create comprehensive English response
            response_text = await format_jobs_with_ai_english(search_results, state_name)
            target_lang = "en"
        else:
            # Use AI to create comprehensive Hindi response
            response_text = await format_jobs_with_ai(search_results, state_name, "hi")
            target_lang = detected_lang if detected_lang != "en" else "hi"

        # Translate to target language if not Hindi or English
        if target_lang not in ["hi", "en"] and not force_english:
            logger.info(f"Translating government jobs to {target_lang}")
            response_text = await translate_response(response_text, target_lang)

        # Calculate total vacancies
        total_vacancies = 0
        for job in jobs_structured:
            if job["vacancies"]:
                try:
                    total_vacancies += int(job["vacancies"].replace(",", ""))
                except ValueError:
                    pass

        return {
            "tool_result": result,
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
            "structured_data": {
                "jobs": jobs_structured,
                "query": state_name or "Central Government",
                "total_jobs": len(jobs_structured),
                "total_vacancies": total_vacancies if total_vacancies > 0 else None,
                "date": datetime.now().strftime("%d %B %Y")
            }
        }

    except Exception as e:
        logger.error(f"Govt jobs handler error: {e}", exc_info=True)
        return {
            "response_text": "सरकारी नौकरी की जानकारी अभी प्राप्त नहीं हो सकी। Could not fetch job openings right now.",
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
