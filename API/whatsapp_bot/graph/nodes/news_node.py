"""
News Node

Fetches and displays news articles based on user query.
Supports multilingual responses (11+ Indian languages).

UPDATED: Now uses AI for response translation and better formatting.
"""

import logging
from datetime import datetime
from whatsapp_bot.state import BotState
from whatsapp_bot.config import settings
from common.tools.news_tool import get_news
from common.utils.response_formatter import sanitize_error, create_service_error_response
from common.i18n.responses import get_news_label, get_phrase

# AI Translation Service
try:
    from common.services.ai_language_service import ai_translate_response
    AI_TRANSLATE_AVAILABLE = True
except ImportError:
    AI_TRANSLATE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Intent constant
INTENT = "get_news"

# Category mapping with emojis
CATEGORY_CONFIG = {
    "national": {"emoji": "🇮🇳", "name": "National News", "name_hi": "राष्ट्रीय समाचार"},
    "international": {"emoji": "🌐", "name": "International News", "name_hi": "अंतर्राष्ट्रीय समाचार"},
    "sports": {"emoji": "🏏", "name": "Sports News", "name_hi": "खेल समाचार"},
    "business": {"emoji": "💼", "name": "Business & Economy", "name_hi": "व्यापार और अर्थव्यवस्था"},
    "technology": {"emoji": "💻", "name": "Technology", "name_hi": "प्रौद्योगिकी"},
    "entertainment": {"emoji": "🎬", "name": "Entertainment", "name_hi": "मनोरंजन"},
    "education": {"emoji": "🎓", "name": "Education", "name_hi": "शिक्षा"},
    "health": {"emoji": "🏥", "name": "Health", "name_hi": "स्वास्थ्य"},
    "science": {"emoji": "🔬", "name": "Science", "name_hi": "विज्ञान"},
    "general": {"emoji": "📰", "name": "Top Headlines", "name_hi": "मुख्य समाचार"},
}


def _categorize_article(article: dict) -> str:
    """Categorize article based on keywords in title/description."""
    title = (article.get("title") or "").lower()
    desc = (article.get("description") or "").lower()
    text = f"{title} {desc}"

    # Keyword-based categorization
    if any(w in text for w in ["india", "delhi", "modi", "parliament", "government", "minister", "bjp", "congress", "election"]):
        return "national"
    if any(w in text for w in ["trump", "us ", "china", "russia", "ukraine", "israel", "pakistan", "world", "global", "international"]):
        return "international"
    if any(w in text for w in ["cricket", "ipl", "match", "sports", "player", "team", "tournament", "olympic", "football", "tennis"]):
        return "sports"
    if any(w in text for w in ["stock", "market", "economy", "business", "company", "investment", "rupee", "sensex", "nifty", "gdp"]):
        return "business"
    if any(w in text for w in ["tech", "ai", "google", "apple", "microsoft", "software", "app", "digital", "cyber", "startup"]):
        return "technology"
    if any(w in text for w in ["movie", "film", "actor", "bollywood", "hollywood", "music", "celebrity", "entertainment"]):
        return "entertainment"
    if any(w in text for w in ["school", "university", "exam", "student", "education", "college", "jee", "neet", "board"]):
        return "education"
    if any(w in text for w in ["health", "hospital", "doctor", "medical", "disease", "covid", "vaccine", "treatment"]):
        return "health"

    return "general"


def _format_news_response(articles: list, detected_lang: str, query: str = "") -> str:
    """Format news articles in a clean, categorized format like Puch AI."""
    today = datetime.now()
    date_str = today.strftime("%d %B %Y")

    # Header
    if detected_lang == "hi":
        header = f"यहां {date_str} की ताज़ा खबरें हैं:"
    else:
        header = f"Here are the latest news headlines for {date_str}:"

    # Categorize articles
    categorized = {}
    for article in articles:
        cat = _categorize_article(article)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(article)

    # Build response
    response_lines = [header, ""]

    # Priority order for categories
    category_order = ["national", "international", "sports", "business", "technology", "education", "entertainment", "health", "science", "general"]

    for cat in category_order:
        if cat not in categorized:
            continue

        cat_articles = categorized[cat][:3]  # Max 3 per category
        if not cat_articles:
            continue

        config = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["general"])
        cat_name = config["name_hi"] if detected_lang == "hi" else config["name"]

        response_lines.append(f"{config['emoji']} *{cat_name}*")

        for i, article in enumerate(cat_articles, 1):
            headline = article.get("title", "").strip()
            url = article.get("url", "").strip()
            source = article.get("source", "").strip()
            description = (article.get("description") or "").strip()

            # Clean up headline (remove source suffix if present)
            if " - " in headline:
                headline = headline.rsplit(" - ", 1)[0]

            # Truncate description
            if description and len(description) > 150:
                description = description[:147] + "..."

            # Format: number. **Headline**: Description
            if description:
                response_lines.append(f"{i}. *{headline}*: {description}")
            else:
                response_lines.append(f"{i}. *{headline}*")

            # Source with link
            if source and url:
                response_lines.append(f"   🔗 {source} [ {url} ]")
            elif url:
                response_lines.append(f"   🔗 [ {url} ]")

        response_lines.append("")  # Empty line between categories

    # Footer
    if detected_lang == "hi":
        response_lines.append("─────────────────")
        response_lines.append("💡 _किसी विषय पर समाचार के लिए टाइप करें_")
    else:
        response_lines.append("─────────────────")
        response_lines.append("💡 _Type a topic to get specific news_")

    return "\n".join(response_lines)


async def handle_news(state: BotState) -> dict:
    """
    Node function: Fetches news articles and formats them for display.
    Returns response in user's detected language using AI translation.

    Args:
        state: Current bot state with extracted entities for news query.

    Returns:
        Updated state with news articles or an error message.
    """
    entities = state.get("extracted_entities", {})
    detected_lang = state.get("detected_language", "en")
    query = entities.get("news_query", "").strip()
    category = entities.get("news_category", "").strip()

    # Also try to get query from current_query if not in entities
    if not query:
        current_query = state.get("current_query", "")
        # Use the normalized query if available (already in English)
        if current_query and "news" not in current_query.lower():
            query = current_query

    logger.info(f"News handler: query={query}, category={category}, lang={detected_lang}")

    if not query and not category:
        # Default to top headlines if no query or category is provided
        category = "general"

    try:
        result = await get_news(query=query, category=category, language=detected_lang)

        if result["success"]:
            articles = result["data"].get("articles", [])
            if not articles:
                response_text = get_news_label("not_found", detected_lang)
            else:
                # Use new formatting function
                response_text = _format_news_response(articles, detected_lang, query)

                # Translate response to user's language using AI
                if detected_lang != "en" and AI_TRANSLATE_AVAILABLE:
                    try:
                        response_text = await ai_translate_response(
                            text=response_text,
                            target_language=detected_lang,
                            openai_api_key=settings.openai_api_key
                        )
                    except Exception as e:
                        logger.warning(f"AI translation failed for news: {e}")

            return {
                "tool_result": result,
                "response_text": response_text,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }
        else:
            raw_error = result.get("error", "")
            try_topic = get_news_label("try_topic", detected_lang)
            return {
                "tool_result": result,
                "response_text": try_topic,
                "response_type": "text",
                "should_fallback": False,
                "intent": INTENT,
            }

    except Exception as e:
        logger.error(f"News handler error: {e}")
        error_msg = get_phrase("error_occurred", detected_lang)
        return {
            "response_text": error_msg,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }
