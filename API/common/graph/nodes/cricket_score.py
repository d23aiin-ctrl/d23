"""
Cricket Score Node

Fetches live cricket scores from the internet and formats them beautifully in multiple languages.
Prioritizes Indian matches and shows live scores with detailed information.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

INTENT = "cricket_score"


def _extract_match_info(result: Dict) -> Dict:
    """Extract cricket match information from search result with improved score extraction."""
    title = result.get("title", "").strip()
    snippet = result.get("snippet", "").strip()
    link = result.get("link", "").strip()

    text = f"{title} {snippet}"

    # Extract teams - improved patterns with multiple attempts
    teams = ""

    # Pattern 1: Full names with vs (India vs New Zealand)
    team_pattern1 = re.compile(r'\b([A-Z][a-zA-Z\s]+?)\s+(?:vs?\.?|v)\s+([A-Z][a-zA-Z\s]+?)(?:\s+(?:live|score|match|T20|ODI|Test|cricket|fixture|schedule|today)|\s*[,:\-]|$)', re.IGNORECASE)
    team_match = team_pattern1.search(text)
    if team_match:
        team1 = team_match.group(1).strip()
        team2 = team_match.group(2).strip()
        # Filter out common false positives
        if team1.lower() not in ['cricket', 'live', 'match', 'score'] and team2.lower() not in ['cricket', 'live', 'match', 'score']:
            teams = f"{team1} vs {team2}"

    # Pattern 2: Short codes (IND vs AUS, IND vs NZ)
    if not teams:
        team_pattern2 = re.compile(r'\b([A-Z]{2,3})\s+vs?\s+([A-Z]{2,3})\b', re.IGNORECASE)
        team_match = team_pattern2.search(text)
        if team_match:
            team1 = team_match.group(1).strip().upper()
            team2 = team_match.group(2).strip().upper()
            teams = f"{team1} vs {team2}"

    # Pattern 3: "India, New Zealand" format
    if not teams:
        team_pattern3 = re.compile(r'\b(India|Pakistan|Australia|England|New Zealand|South Africa|Sri Lanka|Bangladesh|West Indies|Afghanistan|Zimbabwe)\s*,\s*(India|Pakistan|Australia|England|New Zealand|South Africa|Sri Lanka|Bangladesh|West Indies|Afghanistan|Zimbabwe)\b', re.IGNORECASE)
        team_match = team_pattern3.search(text)
        if team_match:
            team1 = team_match.group(1).strip()
            team2 = team_match.group(2).strip()
            teams = f"{team1} vs {team2}"

    # Extract scores - improved patterns to catch more formats
    # Pattern 1: Standard format "234/5" or "156-7"
    score_pattern1 = re.compile(r'\b(\d{2,3})[/-](\d{1,2})\b')
    scores = score_pattern1.findall(text)

    # Pattern 2: With team names "India: 234/5"
    score_with_team = re.compile(r'([A-Z][a-zA-Z\s]+?):\s*(\d{2,3})[/-](\d{1,2})', re.IGNORECASE)
    team_scores_match = score_with_team.findall(text)

    # Extract overs - improved patterns
    over_pattern = re.compile(r'(\d{1,2}(?:\.\d)?)\s*(?:overs?|ov)', re.IGNORECASE)
    overs = over_pattern.findall(text)

    # Check if match is live or scheduled
    is_live = any(keyword in text.lower() for keyword in ['live', 'currently', 'playing', 'in progress', 'ongoing'])
    is_scheduled = any(keyword in text.lower() for keyword in ['scheduled', 'upcoming', 'today', 'tomorrow', 'match starts'])

    # Extract venue/location - improved
    venue_keywords = ['Stadium', 'Ground', 'Oval', 'Park', 'Cricket Club', 'Arena', 'Sports Complex']
    venue = ""
    for keyword in venue_keywords:
        venue_match = re.search(rf'([A-Z][a-zA-Z\s]+{keyword}(?:\s*,\s*[A-Z][a-zA-Z\s]+)?)', text)
        if venue_match:
            venue = venue_match.group(1).strip()
            break

    # Extract time - improved patterns
    time_pattern = re.compile(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm|IST|GMT)?)')
    time_match = time_pattern.search(text)
    match_time = time_match.group(1) if time_match else ""

    # Extract tournament/series
    tournament_keywords = ['IPL', 'T20', 'ODI', 'Test', 'World Cup', 'Champions Trophy', 'Asia Cup', 'T20I', 'Series', 'International']
    tournament = ""
    for keyword in tournament_keywords:
        if keyword.lower() in text.lower():
            tournament = keyword
            break

    # Extract match status (won, lost, tied, abandoned)
    status = ""
    if 'won by' in text.lower():
        status_match = re.search(r'(won by \d+ (?:runs|wickets))', text, re.IGNORECASE)
        if status_match:
            status = status_match.group(1)
    elif 'tied' in text.lower():
        status = "Match tied"
    elif 'abandoned' in text.lower():
        status = "Match abandoned"

    return {
        "title": title,
        "snippet": snippet[:200],
        "link": link,
        "teams": teams,
        "scores": scores,
        "team_scores_match": team_scores_match,
        "overs": overs,
        "venue": venue,
        "time": match_time,
        "tournament": tournament,
        "is_live": is_live,
        "is_scheduled": is_scheduled,
        "status": status,
    }


def format_cricket_scores_hindi(india_matches: List[Dict], live_matches: List[Dict]) -> str:
    """Format cricket scores in concise, conversational Hindi."""
    lines = []

    # Process India matches first (main focus)
    has_india_match = False
    if india_matches:
        for match_info in india_matches[:1]:  # Only top India match
            if match_info["teams"] and "india" in match_info["teams"].lower():
                has_india_match = True

                # Header - short and sweet
                lines.append(f"🏏 *{match_info['teams']}*")

                # Tournament tag inline if available
                if match_info["tournament"]:
                    lines.append(f"_{match_info['tournament']}_")

                lines.append("")

                # Scores - the main info people want
                if match_info["scores"]:
                    for idx, (runs, wickets) in enumerate(match_info["scores"][:2]):
                        team_parts = match_info["teams"].split(" vs ")
                        team_name = team_parts[idx] if idx < len(team_parts) else f"Team {idx+1}"
                        overs_info = f" ({match_info['overs'][idx]} ov)" if idx < len(match_info["overs"]) else ""
                        lines.append(f"*{team_name}:* {runs}/{wickets}{overs_info}")
                elif match_info["team_scores_match"]:
                    for team_name, runs, wickets in match_info["team_scores_match"][:2]:
                        lines.append(f"*{team_name}:* {runs}/{wickets}")
                elif match_info["is_scheduled"]:
                    if match_info["time"]:
                        lines.append(f"⏰ शुरू होगा: {match_info['time']}")
                    else:
                        lines.append("मैच जल्द शुरू होगा")

                # Match result if completed
                if match_info["status"]:
                    lines.append(f"✅ {match_info['status']}")

                # Single link for live score
                if match_info["link"] and match_info["is_live"]:
                    lines.append("")
                    lines.append(f"📺 Live: {match_info['link']}")

                break

    # Other matches - very brief
    other_matches = []
    for match_info in live_matches:
        if match_info["teams"]:
            if has_india_match and "india" in match_info["teams"].lower():
                continue
            other_matches.append(match_info)

    if other_matches and len(other_matches) > 0:
        lines.append("")
        lines.append("*अन्य मैच:*")
        for match in other_matches[:2]:  # Max 2 other matches
            if match["teams"]:
                score_text = ""
                if match["scores"]:
                    score_text = f" - {match['scores'][0][0]}/{match['scores'][0][1]}"
                elif match["team_scores_match"]:
                    score_text = f" - {match['team_scores_match'][0][1]}/{match['team_scores_match'][0][2]}"
                lines.append(f"• {match['teams']}{score_text}")

    if not has_india_match and not other_matches:
        lines.append("अभी कोई लाइव मैच नहीं है।")
        lines.append("Cricbuzz पर चेक करो: cricbuzz.com")

    # Simple follow-up prompt
    lines.append("")
    lines.append("_कोई और टीम का स्कोर चाहिए?_")

    return "\n".join(lines)


def format_cricket_scores_english(india_matches: List[Dict], live_matches: List[Dict]) -> str:
    """Format cricket scores in concise, conversational English."""
    lines = []

    # Process India matches first (main focus)
    has_india_match = False
    if india_matches:
        for match_info in india_matches[:1]:  # Only top India match
            if match_info["teams"] and "india" in match_info["teams"].lower():
                has_india_match = True

                # Header - short and sweet
                lines.append(f"🏏 *{match_info['teams']}*")

                # Tournament tag inline if available
                if match_info["tournament"]:
                    lines.append(f"_{match_info['tournament']}_")

                lines.append("")

                # Scores - the main info people want
                if match_info["scores"]:
                    for idx, (runs, wickets) in enumerate(match_info["scores"][:2]):
                        team_parts = match_info["teams"].split(" vs ")
                        team_name = team_parts[idx] if idx < len(team_parts) else f"Team {idx+1}"
                        overs_info = f" ({match_info['overs'][idx]} ov)" if idx < len(match_info["overs"]) else ""
                        lines.append(f"*{team_name}:* {runs}/{wickets}{overs_info}")
                elif match_info["team_scores_match"]:
                    for team_name, runs, wickets in match_info["team_scores_match"][:2]:
                        lines.append(f"*{team_name}:* {runs}/{wickets}")
                elif match_info["is_scheduled"]:
                    if match_info["time"]:
                        lines.append(f"⏰ Starts: {match_info['time']}")
                    else:
                        lines.append("Match starting soon")

                # Match result if completed
                if match_info["status"]:
                    lines.append(f"✅ {match_info['status']}")

                # Single link for live score
                if match_info["link"] and match_info["is_live"]:
                    lines.append("")
                    lines.append(f"📺 Live: {match_info['link']}")

                break

    # Other matches - very brief
    other_matches = []
    for match_info in live_matches:
        if match_info["teams"]:
            if has_india_match and "india" in match_info["teams"].lower():
                continue
            other_matches.append(match_info)

    if other_matches and len(other_matches) > 0:
        lines.append("")
        lines.append("*Other matches:*")
        for match in other_matches[:2]:  # Max 2 other matches
            if match["teams"]:
                score_text = ""
                if match["scores"]:
                    score_text = f" - {match['scores'][0][0]}/{match['scores'][0][1]}"
                elif match["team_scores_match"]:
                    score_text = f" - {match['team_scores_match'][0][1]}/{match['team_scores_match'][0][2]}"
                lines.append(f"• {match['teams']}{score_text}")

    if not has_india_match and not other_matches:
        lines.append("No live matches right now.")
        lines.append("Check cricbuzz.com for updates")

    # Simple follow-up prompt
    lines.append("")
    lines.append("_Want another team's score?_")

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
    # Skip if already Hindi or English
    if lang_code in ["en", "hi"] or lang_code not in LANGUAGE_NAMES:
        return text

    try:
        lang_info = LANGUAGE_NAMES.get(lang_code, {})
        language_name = lang_info.get("en", "English")

        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a translator. Translate the following cricket score information to {language_name} ({language_code}).

Keep the formatting with bullets and asterisks (*) intact.
Use the appropriate script for the language (e.g., Kannada script for Kannada, Tamil script for Tamil).
Keep team names, scores, URLs in original format (readable for the target language).
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


async def handle_cricket_score(state: BotState) -> dict:
    """
    Handle cricket score queries by fetching real-time data from the internet.

    Supports:
    - Live cricket scores from all matches
    - Prioritizes Indian matches (always searches for India matches first)
    - Multi-language responses (Hindi/English/regional)
    - Real-time updated scores
    - Tournament, venue, time information
    - Streaming platform information
    """
    user_message = state.get("current_query", "").strip()
    detected_lang = state.get("detected_language", "en")

    try:
        # Check if user explicitly wants English
        query_lower = user_message.lower() if user_message else ""
        force_english = any(kw in query_lower for kw in ["in english", "english mein", "english me"])

        logger.info(f"Fetching cricket scores with India matches prioritized")

        # Search 1: India fixtures and matches specifically
        india_search_query = (
            "India vs cricket match today fixture schedule 2026 IND "
            "site:cricbuzz.com OR site:espncricinfo.com"
        )

        # Search 2: India live scores
        india_live_query = (
            "India cricket live score today 2026 IND vs "
            "site:cricbuzz.com OR site:espncricinfo.com"
        )

        # Search 3: All live matches globally
        live_search_query = (
            "live cricket score today 2026 match scorecard "
            "site:cricbuzz.com OR site:espncricinfo.com OR site:cricheroes.com"
        )

        # Fetch all three searches
        india_result = await search_google(query=india_search_query, max_results=10, country="in", locale="en")
        india_live_result = await search_google(query=india_live_query, max_results=10, country="in", locale="en")
        live_result = await search_google(query=live_search_query, max_results=8, country="in", locale="en")

        # Extract results
        india_search_results = []
        if india_result["success"]:
            india_search_results = (india_result.get("data") or {}).get("results", [])

        india_live_results = []
        if india_live_result["success"]:
            india_live_results = (india_live_result.get("data") or {}).get("results", [])

        live_search_results = []
        if live_result["success"]:
            live_search_results = (live_result.get("data") or {}).get("results", [])

        # Combine India-specific searches
        combined_india_results = india_search_results + india_live_results

        if not combined_india_results and not live_search_results:
            return {
                "response_text": "कोई क्रिकेट स्कोर की जानकारी नहीं मिली। कृपया कुछ देर बाद प्रयास करें।",
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

        # Extract match information for India matches
        india_matches = []
        seen_links = set()  # To avoid duplicates

        for result in combined_india_results:
            link = result.get("link", "")
            if link and link in seen_links:
                continue  # Skip duplicate

            match_info = _extract_match_info(result)

            # Only add if it's an India match
            teams_lower = match_info["teams"].lower() if match_info["teams"] else ""
            if "india" in teams_lower or "ind" in teams_lower:
                if match_info["teams"] or match_info["scores"]:
                    india_matches.append(match_info)
                    if link:
                        seen_links.add(link)

        live_matches = []
        for result in live_search_results:
            match_info = _extract_match_info(result)
            if match_info["teams"] or match_info["scores"]:
                live_matches.append(match_info)

        logger.info(f"Found {len(india_matches)} India matches and {len(live_matches)} live matches")

        # Debug logging
        if india_matches:
            for idx, match in enumerate(india_matches[:3]):
                logger.info(f"India Match {idx+1}: {match['teams']} | Live: {match['is_live']} | Scheduled: {match['is_scheduled']}")
        else:
            logger.warning("No India matches found! Check search results.")

        # Format results
        if force_english:
            response_text = format_cricket_scores_english(india_matches, live_matches)
            target_lang = "en"
        else:
            # Default to Hindi for Indian cricket matches
            response_text = format_cricket_scores_hindi(india_matches, live_matches)
            target_lang = detected_lang if detected_lang != "en" else "hi"

        # Translate to target language if not Hindi or English
        if target_lang not in ["hi", "en"] and not force_english:
            logger.info(f"Translating cricket scores to {target_lang}")
            response_text = await translate_response(response_text, target_lang)

        return {
            "tool_result": india_result,  # Return primary search result
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Cricket score handler error: {e}", exc_info=True)
        return {
            "response_text": "क्रिकेट स्कोर अभी प्राप्त नहीं हो सके। Could not fetch cricket scores right now.",
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
