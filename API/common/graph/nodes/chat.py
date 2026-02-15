"""
General Chat Node

Handles general conversation using GPT-4o-mini with smart AI capabilities.
Falls back handler when no specific intent is matched.
Supports multi-language responses with personality adaptation.

Enhanced with:
- Conversation memory for multi-turn context
- Personality adaptation based on language
- Smart fallback with error recovery
- Time-aware responses
"""

import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime

from common.graph.state import BotState
from common.config.settings import settings
from common.utils.response_formatter import sanitize_error
from common.i18n.constants import LANGUAGE_NAMES

# Import smart AI capabilities
from common.graph.nodes.smart_ai import (
    ConversationMemory,
    smart_chat_sync,
    smart_fallback,
    get_personality,
    enhance_response,
    get_error_recovery,
)

# Import web search for current events
try:
    from common.tools.serper_search import search_google
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    search_google = None

logger = logging.getLogger(__name__)

# Intent constant
INTENT = "chat"


def _is_recent_news_query(message: str) -> tuple[bool, str]:
    """
    Detect if the query is about recent news/events or factual information
    that would benefit from web search.

    Returns:
        (should_web_search, search_query_for_web)
    """
    msg_lower = message.lower()

    # News/current event indicators - expanded list
    news_indicators = [
        # Why/what happened questions
        "kyon chhora", "kyun chhora", "kyu chhora", "why left", "why did",
        "kyon nikla", "kyun nikla", "why resigned", "why quit",
        "kya hua", "kya ho gaya", "what happened", "latest news",
        "क्यों छोड़ा", "क्या हुआ", "क्यों निकला",
        # Time indicators
        "recent", "abhi", "aaj", "kal", "yesterday", "today",
        "2024", "2025", "2026", "last week", "last month", "this week", "this month",
        "हाल ही", "आज", "कल", "अभी",
        # News/information requests
        "news", "khabar", "खबर", "समाचार", "update", "latest",
        # Who/what is questions
        "who is", "what is", "kaun hai", "kya hai", "कौन है", "क्या है",
        # Current affairs
        "election", "budget", "policy", "government", "minister",
        "chunav", "sarkar", "mantri", "चुनाव", "सरकार", "मंत्री",
        # Business/company news
        "company", "ceo", "founder", "startup", "ipo", "share", "stock",
        "acquisition", "merger", "funding", "layoff",
        # Sports
        "match", "score", "won", "lost", "tournament", "championship",
        # Entertainment
        "movie", "film", "actor", "actress", "release", "trailer",
        # Tell me about / explain
        "tell me about", "batao", "बताओ", "explain", "samjhao", "समझाओ",
    ]

    # Check for news indicators
    is_news = any(ind in msg_lower for ind in news_indicators)

    # Also check if it's a question that would benefit from web search
    question_patterns = [
        r"\b(who|what|when|where|why|how)\b",  # English questions
        r"\b(kaun|kya|kab|kahan|kyon|kaise)\b",  # Hindi Hinglish
        r"\b(कौन|क्या|कब|कहाँ|क्यों|कैसे)\b",  # Hindi script
        # Tamil
        r"\b(yaar|yaru|enna|eppo|enga|en|eppadi)\b",  # Tamil transliterated
        r"\b(யார்|என்ன|எப்போது|எங்கே|ஏன்|எப்படி)\b",  # Tamil script
        # Telugu
        r"\b(evaru|emiti|eppudu|ekkada|enduku|ela)\b",  # Telugu transliterated
        r"\b(ఎవరు|ఏమిటి|ఎప్పుడు|ఎక్కడ|ఎందుకు|ఎలా)\b",  # Telugu script
        # Bengali
        r"\b(ke|ki|kokhon|kothay|keno|kibhabe)\b",  # Bengali transliterated
        r"\b(কে|কি|কখন|কোথায়|কেন|কিভাবে)\b",  # Bengali script
        # Kannada
        r"\b(yaaru|yenu|yaavaga|elli|yaake|hege)\b",  # Kannada transliterated
        r"\b(ಯಾರು|ಏನು|ಯಾವಾಗ|ಎಲ್ಲಿ|ಯಾಕೆ|ಹೇಗೆ)\b",  # Kannada script
        # Malayalam
        r"\b(aaru|enthu|eppol|evide|enthinu|engane)\b",  # Malayalam transliterated
        r"\b(ആരു|എന്ത്|എപ്പോൾ|എവിടെ|എന്തിന്|എങ്ങനെ)\b",  # Malayalam script
        # Marathi
        r"\b(kon|kay|kevha|kuthe|ka|kasa)\b",  # Marathi transliterated
        r"\b(कोण|काय|केव्हा|कुठे|का|कसा)\b",  # Marathi script
        # Gujarati
        r"\b(kon|shu|kyare|kya|kem|kevi)\b",  # Gujarati transliterated
        r"\b(કોણ|શું|ક્યારે|ક્યાં|કેમ|કેવી)\b",  # Gujarati script
        # Punjabi
        r"\b(kaun|ki|kadho|kithe|kion|kive)\b",  # Punjabi transliterated
        r"\b(ਕੌਣ|ਕੀ|ਕਦੋਂ|ਕਿੱਥੇ|ਕਿਉਂ|ਕਿਵੇਂ)\b",  # Punjabi script
        # About/tell me patterns in various languages
        r"\b(batao|bolo|about|bare me|baare mein|gurinchi|patti|bagge)\b",
    ]

    import re
    is_question = any(re.search(p, msg_lower) for p in question_patterns)

    if not is_news and not is_question:
        return False, ""

    # Build a search query from the message
    # Try to extract person/company name for search
    patterns = [
        r"(\w+)\s+(?:ne|ने)\s+(\w+)\s+(?:kyon|kyun|kyu|क्यों)",  # "Deepinder ne Zomato kyon"
        r"why\s+did\s+(\w+)\s+(?:leave|quit|resign)\s+(\w+)?",  # "why did X leave Y"
        r"(\w+)\s+(?:kya hua|kya ho gaya|क्या हुआ)",  # "X kya hua"
        r"what\s+happened\s+(?:to|with)\s+(\w+)",  # "what happened to X"
        r"who\s+is\s+(\w+)",  # "who is X"
        r"(\w+)\s+kaun\s+hai",  # "X kaun hai"
        r"tell\s+me\s+about\s+(\w+)",  # "tell me about X"
        r"(\w+)\s+ke\s+bare\s+me",  # "X ke bare me"
    ]

    search_query = message + " latest news"  # Default to full message + news
    for pattern in patterns:
        match = re.search(pattern, msg_lower)
        if match:
            # Build search query from extracted entities
            groups = [g for g in match.groups() if g]
            if groups:
                search_query = " ".join(groups) + " latest news 2026"
            break

    return True, search_query


async def _perform_web_search(query: str, max_results: int = 10) -> str:
    """
    Perform web search and return formatted results for LLM context.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        Formatted search results string for LLM context
    """
    if not WEB_SEARCH_AVAILABLE or not search_google:
        return ""

    try:
        result = await search_google(query, max_results=max_results)

        # ToolResult is a TypedDict, access as dict
        if not result.get("success") or not result.get("data"):
            logger.warning(f"Web search failed: {result.get('error')}")
            return ""

        data = result.get("data", {})
        formatted = []

        # Include answer box if available (prominent)
        if data.get("answer"):
            formatted.append(f"=== QUICK ANSWER ===\n{data['answer']}\n")

        # Include knowledge graph info
        if data.get("knowledge_graph"):
            kg = data["knowledge_graph"]
            formatted.append("=== KNOWLEDGE GRAPH ===")
            if kg.get("title"):
                formatted.append(f"Title: {kg.get('title')}")
            if kg.get("type"):
                formatted.append(f"Type: {kg.get('type')}")
            if kg.get("description"):
                formatted.append(f"Description: {kg.get('description')}")
            if kg.get("attributes"):
                for key, value in kg.get("attributes", {}).items():
                    formatted.append(f"{key}: {value}")
            formatted.append("")

        # Include ALL search results with FULL details
        results = data.get("results", [])
        if results:
            formatted.append("=== WEB SEARCH RESULTS ===")
            formatted.append(f"(Found {len(results)} results - USE ALL THIS INFORMATION)\n")
            for i, item in enumerate(results, 1):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                formatted.append(f"--- Result {i} ---")
                formatted.append(f"Title: {title}")
                if snippet:
                    formatted.append(f"Content: {snippet}")
                if link:
                    formatted.append(f"URL: {link}")
                formatted.append("")

        # Include related searches for context
        related = data.get("related_searches", [])
        if related:
            formatted.append("=== RELATED TOPICS ===")
            for item in related[:5]:
                if isinstance(item, dict):
                    formatted.append(f"- {item.get('query', '')}")
                else:
                    formatted.append(f"- {item}")

        return "\n".join(formatted)

    except Exception as e:
        logger.error(f"Web search error: {e}")
        return ""


def _perform_web_search_sync(query: str, max_results: int = 5) -> str:
    """Synchronous wrapper for web search."""
    import asyncio
    try:
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # If we get here, we're in an async context
            # Create a new thread to run the async function
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    _perform_web_search(query, max_results)
                )
                return future.result(timeout=30)
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(_perform_web_search(query, max_results))
    except Exception as e:
        logger.error(f"Web search sync wrapper error: {e}")
        return ""


# Enhanced chat prompt with better personality and context
SMART_CHAT_PROMPT = """You are a super helpful WhatsApp assistant for Indian users. Think of yourself as a knowledgeable friend who's always ready to help - not a formal robot.

## CRITICAL: KNOWLEDGE CUTOFF HANDLING
Your knowledge has a cutoff date. NEVER respond with:
- "I am trained on data up to [date]"
- "My knowledge cutoff is [date]"
- "I don't have information after [date]"

Instead, if asked about recent events, news, or things you don't know:
1. Acknowledge you may not have the latest info
2. Provide what context you DO know (if any)
3. ALWAYS suggest: "Try asking 'news about [topic]' for the latest updates!"
4. Be helpful, not dismissive

Example BAD response: "आप अक्टूबर 2023 तक के डेटा पर प्रशिक्षित हैं।"
Example GOOD response: "इस बारे में मेरे पास नवीनतम जानकारी नहीं है। 'Zomato news' या 'Deepinder Goyal news' पूछकर latest updates पाएं!"

## YOUR PERSONALITY
{personality_style}

## CONVERSATION CONTEXT
{conversation_context}

## CAPABILITIES YOU CAN HELP WITH
• *Local Search* - Find restaurants, hospitals, ATMs, shops (say: "restaurants near Connaught Place")
• *Weather* - Any city's weather (say: "weather Delhi" or share location)
• *Indian Railways* - PNR status & live train tracking (say: "PNR 1234567890" or "train 12301 status")
• *Cricket* - Live scores & match updates
• *Stocks* - Share prices & market info (say: "Reliance stock price")
• *News* - Latest headlines
• *Horoscope* - Daily predictions (say: "Aries horoscope")
• *Govt Jobs* - Latest sarkari naukri updates
• *Images* - Generate AI art (say: "generate image of sunset on beach")
• *General Chat* - Ask me anything!

## HOW TO RESPOND
1. Be natural - write like you're texting a friend
2. Be concise - WhatsApp has limits, respect them
3. Be proactive - if you can guess what they need, offer it
4. Be helpful - guide with examples when they're stuck
5. Match their energy - casual question = casual answer
6. Minimal emojis - one or two max, don't overdo it
7. For travel plans - give day-wise routes with places to stay

## TIME CONTEXT
It's {time_of_day} on {day_of_week}. Be naturally aware of this.

## LANGUAGE
Respond in {language_name} ({language_code}). Use the appropriate script.
For Hindi/Hinglish:
- Use POLITE form "आप" (aap), NEVER use informal "तुम" (tum)
- Be respectful but warm - like talking to someone you respect
- Example: "आप कैसे हैं?" NOT "तुम कैसे हो?"
- Example: "आपको क्या चाहिए?" NOT "तुझे क्या चाहिए?"

Remember: You're a helpful, respectful assistant - polite but warm!"""


# Language code to full name mapping for prompt
def get_language_instruction(lang_code: str) -> tuple:
    """Get language name and code for prompt."""
    lang_info = LANGUAGE_NAMES.get(lang_code, {"en": "English", "native": "English"})
    return lang_info.get("en", "English"), lang_code


def _get_time_context() -> tuple:
    """Get time of day and day of week for context."""
    now = datetime.now()
    hour = now.hour

    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week = days[now.weekday()]

    return time_of_day, day_of_week


def handle_chat(state: BotState) -> dict:
    """
    Smart chat handler with personality and context awareness.

    Features:
    - Uses conversation memory for multi-turn context
    - Adapts personality based on detected language
    - Time-aware natural responses
    - Stores exchanges for follow-up handling

    Args:
        state: Current bot state

    Returns:
        Updated state with intelligent chat response
    """
    user_message = (
        state.get("current_query", "")
        or state["whatsapp_message"].get("text", "")
    )

    # Get user info
    phone = state["whatsapp_message"].get("from_number", "unknown")
    detected_lang = state.get("detected_language", "en")
    language_name, language_code = get_language_instruction(detected_lang)

    logger.info(f"Smart chat handler - phone: {phone[-4:]}, lang: {language_name}")

    # Get conversation memory for this user
    memory = ConversationMemory.get_or_create(phone)

    # Get personality for this language
    personality = get_personality(detected_lang)

    # Get time context
    time_of_day, day_of_week = _get_time_context()

    # Handle empty message
    if not user_message:
        greetings = {
            "en": "Hey! How can I help you today?",
            "hi": "हेलो! कैसे मदद करूं आज?",
            "bn": "হ্যালো! আজ কিভাবে সাহায্য করতে পারি?",
            "ta": "வணக்கம்! இன்று எப்படி உதவ முடியும்?",
            "te": "హలో! ఈరోజు ఎలా సహాయం చేయగలను?",
        }
        welcome_msg = greetings.get(detected_lang, greetings["en"])
        return {
            "response_text": welcome_msg,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    # Check if this is a query about recent news/events
    is_news_query, suggested_topic = _is_recent_news_query(user_message)

    try:
        # Build context-aware prompt
        system_prompt = SMART_CHAT_PROMPT.format(
            personality_style=personality.get("style", "friendly and helpful"),
            conversation_context=memory.get_context_summary(),
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            language_name=language_name,
            language_code=language_code,
        )

        # For news/current events queries, perform web search first
        web_search_results = ""
        if is_news_query and WEB_SEARCH_AVAILABLE:
            logger.info(f"News query detected, performing web search for: {suggested_topic}")
            web_search_results = _perform_web_search_sync(suggested_topic, max_results=10)  # Get more results
            if web_search_results:
                logger.info(f"Web search returned results for news query")

        # Add news query context if detected
        if is_news_query:
            if web_search_results:
                # We have web search results - use them!
                news_guidance = f"""

## IMPORTANT: CURRENT NEWS/EVENTS QUERY - USE WEB SEARCH RESULTS
The user is asking about recent news/events. I have searched the web for you.

### WEB SEARCH RESULTS (USE THIS INFORMATION):
{web_search_results}

### YOUR TASK - PROVIDE A COMPREHENSIVE, DETAILED RESPONSE:
1. Create a DETAILED, WELL-STRUCTURED response with multiple sections
2. Use the following format:

   **[Main headline/summary - 2-3 lines]**

   🔹 **मुख्य कारण / Main Reason:**
   • Bullet point 1
   • Bullet point 2
   • Source link: [Title](URL)

   🔄 **क्या बदलाव हुए / What Changed:**
   • Details about changes
   • New appointments, dates, etc.
   • Source link: [Title](URL)

   📌 **महत्वपूर्ण बिंदु / Key Points:**
   • Important fact 1
   • Important fact 2
   • Important fact 3

   🔗 **और पढ़ें / Read More:**
   • [Source 1 Title](URL)
   • [Source 2 Title](URL)

3. Extract ALL relevant details from the search results - be COMPREHENSIVE
4. Include MULTIPLE source links embedded in the content
5. Use emojis for section headers (🔹, 🔄, 📌, 🚀, 🔗)
6. Add "| 🌐 powered by web-search" at the very end
7. Response should be DETAILED (at least 300-400 words equivalent)
8. Do NOT summarize too briefly - give FULL details
"""
            else:
                # No web search results - guide user to news feature
                news_guidance = f"""

## IMPORTANT: THIS IS A NEWS/CURRENT EVENTS QUERY
The user is asking about something that may have happened recently.
- Do NOT say "I'm trained on data up to..." or any cutoff date
- Instead, provide what context you know (if any) and ALWAYS suggest:
  - In Hindi: "'news {suggested_topic}' या '{suggested_topic} news' पूछें latest updates के लिए!"
  - In English: "Try 'news {suggested_topic}' or '{suggested_topic} news' for the latest updates!"
- Be helpful, acknowledge you may not have the latest info, but guide them to get it.
"""
            system_prompt += news_guidance

        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.8,  # Slightly higher for more natural variation
            api_key=settings.OPENAI_API_KEY,
        )

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        response_text = response.content

        # Store this exchange in memory for future context
        memory.add_exchange(
            user_message=user_message,
            bot_response=response_text,
            intent="chat",
            entities=state.get("extracted_entities", {}),
            language=detected_lang
        )

        return {
            "response_text": response_text,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }

    except Exception as e:
        logger.error(f"Smart chat handler error: {e}")

        # Even errors should sound human
        error_responses = {
            "en": "Oops, brain freeze! Ask me again?",
            "hi": "अरे, थोड़ी गड़बड़! फिर से पूछो?",
            "bn": "ওহো, একটু সমস্যা! আবার জিজ্ঞাসা করুন?",
            "ta": "அச்சச்சோ, சிறிய பிரச்சனை! மீண்டும் கேளுங்கள்?",
        }
        fallback_msg = error_responses.get(detected_lang, error_responses["en"])

        return {
            "error": str(e),
            "response_text": fallback_msg,
            "response_type": "text",
            "should_fallback": False,
            "intent": INTENT,
        }


def handle_fallback(state: BotState) -> dict:
    """
    Smart fallback handler with context-aware error recovery.

    Instead of a generic "oops" message, this:
    - Analyzes what went wrong
    - Provides specific guidance based on the failed intent
    - Offers relevant alternatives
    - Uses AI for complex recovery scenarios

    Args:
        state: Current bot state with error info

    Returns:
        Updated state with intelligent recovery response
    """
    error = state.get("error", "")
    original_intent = state.get("intent", "unknown")
    user_message = state.get("current_query", "") or state["whatsapp_message"].get("text", "")
    phone = state["whatsapp_message"].get("from_number", "unknown")
    detected_lang = state.get("detected_language", "en")

    # Log for debugging
    logger.warning(f"Smart fallback - intent: {original_intent}, error: {error[:100] if error else 'None'}")

    # Get conversation memory
    memory = ConversationMemory.get_or_create(phone)

    # Analyze error type
    error_lower = (error or "").lower()

    if "location" in error_lower or "city" in error_lower:
        error_type = "missing_location"
    elif "api" in error_lower or "timeout" in error_lower or "connection" in error_lower:
        error_type = "api_error"
    elif "invalid" in error_lower or "not found" in error_lower:
        error_type = "invalid_input"
    elif "pnr" in error_lower:
        error_type = "invalid_pnr"
    elif "train" in error_lower:
        error_type = "invalid_train"
    else:
        error_type = "generic"

    # Try to get quick recovery message
    quick_recovery = get_error_recovery(original_intent, error_type)

    # Check if we can help by inferring from context
    if error_type == "missing_location" and original_intent in ["weather", "local_search"]:
        inferred_city = memory.infer_missing_entity(original_intent, "city")
        if inferred_city:
            if detected_lang == "hi":
                quick_recovery = f"क्या {inferred_city} का मतलब था? या कोई और जगह बताओ!"
            else:
                quick_recovery = f"Did you mean {inferred_city}? Or tell me a different place!"

    # For known error types, use quick recovery (faster, no API call)
    if error_type != "generic":
        # Translate to Hindi if needed
        if detected_lang == "hi":
            quick_recovery = _translate_to_hindi(quick_recovery)

        return {
            "response_text": quick_recovery,
            "response_type": "text",
            "should_fallback": False,
            "intent": original_intent,
        }

    # For complex/unknown errors, use AI for intelligent recovery
    try:
        language_name, language_code = get_language_instruction(detected_lang)

        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )

        recovery_prompt = f"""You are a WhatsApp assistant. Something went wrong processing the user's request.

User wanted: {original_intent}
User said: "{user_message}"
Error: {error[:200] if error else "Unknown issue"}

Your job:
1. Briefly acknowledge the hiccup (don't over-apologize)
2. If you can answer their question directly, do it!
3. If you need more info, ask specifically
4. Suggest what they can try instead

Conversation context:
{memory.get_context_summary()}

Respond in {language_name}. Be helpful and natural, not robotic."""

        response = llm.invoke([HumanMessage(content=recovery_prompt)])

        return {
            "response_text": response.content,
            "response_type": "text",
            "should_fallback": False,
            "intent": original_intent,
        }

    except Exception as e:
        logger.error(f"Smart fallback AI error: {e}")

        # Ultimate fallback - still be helpful, not generic
        ultimate_fallback = {
            "en": "Hit a snag! Let me try differently - what do you need?\n\n• Weather → 'Weather Delhi'\n• Train → 'PNR 1234567890'\n• Search → 'Restaurants near me'\n• News → 'Latest news'",
            "hi": "थोड़ी गड़बड़! बताओ क्या चाहिए?\n\n• मौसम → 'Weather Delhi'\n• ट्रेन → 'PNR 1234567890'\n• सर्च → 'Restaurants near me'\n• न्यूज़ → 'Latest news'"
        }

        return {
            "response_text": ultimate_fallback.get(detected_lang, ultimate_fallback["en"]),
            "response_type": "text",
            "should_fallback": False,
            "intent": "fallback",
        }


def _translate_to_hindi(text: str) -> str:
    """Quick Hindi translation for common fallback phrases."""
    translations = {
        "Which city's weather should I check?": "किस शहर का मौसम बताऊं?",
        "Or share your location for local weather!": "या अपनी लोकेशन शेयर करो!",
        "Weather service is taking a break.": "मौसम सर्विस में थोड़ी दिक्कत है।",
        "Try again in a bit?": "थोड़ी देर में ट्राई करो?",
        "Or ask me something else!": "या कुछ और पूछो!",
        "That doesn't look like a valid PNR.": "ये PNR सही नहीं लग रहा।",
        "PNR is a 10-digit number from your ticket.": "PNR टिकट पर 10 अंकों का नंबर होता है।",
        "Example:": "जैसे:",
        "IRCTC is being slow.": "IRCTC थोड़ा स्लो है।",
        "What else can I help with?": "और क्या हेल्प करूं?",
        "I need the train number": "ट्रेन नंबर बताओ",
        "Which train are you tracking?": "कौन सी ट्रेन ट्रैक करनी है?",
        "Share your location or tell me the area": "लोकेशन शेयर करो या एरिया बताओ",
        "Couldn't find that nearby.": "पास में नहीं मिला।",
        "Try being more specific?": "थोड़ा स्पेसिफिक बताओ?",
        "No live match right now.": "अभी कोई लाइव मैच नहीं।",
        "Want yesterday's highlights or upcoming schedule?": "कल की हाइलाइट्स या आने वाला शेड्यूल?",
        "Which stock?": "कौन सा स्टॉक?",
        "Give me the name or symbol": "नाम या सिंबल बताओ",
        "Couldn't create that image.": "वो इमेज नहीं बन पाई।",
        "Try a simpler description?": "थोड़ा सिंपल बताओ?",
        "Hit a snag there.": "थोड़ी गड़बड़ हो गई।",
        "Could you rephrase or try something else?": "फिर से बताओ या कुछ और पूछो?",
    }

    result = text
    for eng, hindi in translations.items():
        result = result.replace(eng, hindi)
    return result
