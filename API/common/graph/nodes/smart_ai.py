"""
Smart AI Module for WhatsApp Bot

This module provides intelligent, human-like responses using AI.
Features:
- Context-aware conversation handling
- Smart fallback with error recovery
- Multi-turn conversation memory
- Personality adaptation based on language/context
- Intelligent response enhancement
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from common.graph.state import BotState
from common.config.settings import settings
from common.i18n.constants import LANGUAGE_NAMES

logger = logging.getLogger(__name__)

# =============================================================================
# CONVERSATION MEMORY
# =============================================================================

class ConversationMemory:
    """
    Enhanced conversation memory for multi-turn context tracking.
    Stores last N exchanges with entities and topics.
    """

    _instances: Dict[str, "ConversationMemory"] = {}
    MAX_HISTORY = 10
    MAX_AGE_SECONDS = 1800  # 30 minutes

    def __init__(self, phone: str):
        self.phone = phone
        self.messages: List[Dict[str, Any]] = []
        self.entities: Dict[str, Any] = {}  # Accumulated entities
        self.topic: Optional[str] = None  # Current conversation topic
        self.last_intent: Optional[str] = None
        self.user_preferences: Dict[str, Any] = {}
        self.created_at = time.time()
        self.last_updated = time.time()

    @classmethod
    def get_or_create(cls, phone: str) -> "ConversationMemory":
        """Get existing memory or create new one."""
        if phone in cls._instances:
            memory = cls._instances[phone]
            # Check if memory is too old
            if time.time() - memory.last_updated > cls.MAX_AGE_SECONDS:
                memory.clear()
            return memory
        memory = cls(phone)
        cls._instances[phone] = memory
        return memory

    def add_exchange(
        self,
        user_message: str,
        bot_response: str,
        intent: str,
        entities: Dict[str, Any],
        language: str = "en"
    ):
        """Add a conversation exchange."""
        self.messages.append({
            "user": user_message,
            "bot": bot_response[:500],  # Truncate for memory efficiency
            "intent": intent,
            "entities": entities,
            "language": language,
            "timestamp": time.time()
        })

        # Keep only last N messages
        if len(self.messages) > self.MAX_HISTORY:
            self.messages = self.messages[-self.MAX_HISTORY:]

        # Accumulate entities
        self.entities.update(entities)
        self.last_intent = intent
        self.last_updated = time.time()

        # Update topic based on intent
        topic_mapping = {
            "weather": "weather",
            "cricket_score": "sports",
            "get_news": "news",
            "stock_price": "finance",
            "pnr_status": "travel",
            "train_status": "travel",
            "get_horoscope": "astrology",
            "birth_chart": "astrology",
            "govt_jobs": "jobs",
            "local_search": "search",
        }
        if intent in topic_mapping:
            self.topic = topic_mapping[intent]

    def get_context_summary(self) -> str:
        """Get a summary of conversation context for AI."""
        if not self.messages:
            return "No previous conversation history."

        recent = self.messages[-5:]  # Last 5 exchanges
        summary_parts = []

        for msg in recent:
            summary_parts.append(f"User: {msg['user'][:100]}")
            summary_parts.append(f"Bot: {msg['bot'][:100]}")

        entity_str = ", ".join(f"{k}={v}" for k, v in self.entities.items() if v)

        return f"""Recent conversation ({len(recent)} exchanges):
{chr(10).join(summary_parts)}

Known entities: {entity_str or 'None'}
Current topic: {self.topic or 'General'}
Last intent: {self.last_intent or 'Unknown'}"""

    def infer_missing_entity(self, intent: str, needed_entity: str) -> Optional[Any]:
        """Try to infer a missing entity from conversation history."""
        # If asking about weather and we know a city from recent context
        if intent == "weather" and needed_entity == "city":
            return self.entities.get("city") or self.entities.get("location")

        # If asking about trains and we have train number
        if intent in ["train_status", "pnr_status"] and needed_entity == "train_number":
            return self.entities.get("train_number")

        # If asking about stocks and we have a symbol
        if intent == "stock_price" and needed_entity == "symbol":
            return self.entities.get("stock_symbol") or self.entities.get("symbol")

        return self.entities.get(needed_entity)

    def clear(self):
        """Clear conversation memory."""
        self.messages = []
        self.entities = {}
        self.topic = None
        self.last_intent = None
        self.last_updated = time.time()


# =============================================================================
# PERSONALITY SYSTEM
# =============================================================================

PERSONALITY_TEMPLATES = {
    "en": {
        "greeting": ["Hey!", "Hi there!", "Hello!"],
        "acknowledgment": ["Got it!", "Sure thing!", "Absolutely!"],
        "thinking": ["Let me check...", "Looking into it...", "One moment..."],
        "apology": ["Oops, my bad!", "Sorry about that!", "Let me fix that!"],
        "encouragement": ["You got this!", "Great question!", "I'm here to help!"],
        "style": "friendly and casual, like texting a helpful friend"
    },
    "hi": {
        "greeting": ["नमस्ते!", "हेलो!", "जी, बताइए!"],
        "acknowledgment": ["जी बिल्कुल!", "जी हां!", "ठीक है जी!"],
        "thinking": ["देखता हूं...", "चेक करता हूं...", "एक मिनट..."],
        "apology": ["माफ कीजिए!", "क्षमा करें!", "सॉरी!"],
        "encouragement": ["बढ़िया सवाल!", "मैं हूं ना!", "बताइए, क्या मदद करूं?"],
        "style": "warm, respectful and conversational in Hinglish. ALWAYS use polite आप form, NEVER use तुम/तू. Be like a respectful helpful friend."
    },
    "bn": {
        "greeting": ["হ্যালো!", "নমস্কার!"],
        "acknowledgment": ["ঠিক আছে!", "অবশ্যই!"],
        "thinking": ["দেখছি...", "একটু অপেক্ষা করুন..."],
        "apology": ["দুঃখিত!", "সরি!"],
        "style": "polite and helpful in Bengali"
    },
    "ta": {
        "greeting": ["வணக்கம்!", "ஹாய்!"],
        "acknowledgment": ["சரி!", "நிச்சயமாக!"],
        "thinking": ["பார்க்கிறேன்...", "ஒரு நிமிடம்..."],
        "apology": ["மன்னிக்கவும்!", "சாரி!"],
        "style": "respectful and warm in Tamil"
    },
    "te": {
        "greeting": ["హలో!", "నమస్కారం!"],
        "acknowledgment": ["సరే!", "తప్పకుండా!"],
        "thinking": ["చూస్తున్నాను...", "ఒక్క నిమిషం..."],
        "apology": ["క్షమించండి!", "సారీ!"],
        "style": "friendly and respectful in Telugu"
    }
}

def get_personality(lang_code: str) -> Dict[str, Any]:
    """Get personality template for language."""
    return PERSONALITY_TEMPLATES.get(lang_code, PERSONALITY_TEMPLATES["en"])


# =============================================================================
# SMART CHAT PROMPTS
# =============================================================================

SMART_CHAT_SYSTEM_PROMPT = """You are a super helpful WhatsApp assistant for Indian users. Think of yourself as a smart friend who's always ready to help.

## YOUR PERSONALITY
{personality_style}

## CONVERSATION CONTEXT
{conversation_context}

## YOUR CAPABILITIES
You can help with:
- Local search (restaurants, hospitals, ATMs, shops nearby)
- Weather updates for any city
- Indian Railways (PNR status, train running status)
- Cricket scores and sports updates
- Stock prices and market info
- News headlines
- Horoscope and astrology
- Government jobs and schemes
- Image generation (AI art)
- General questions and chat

## RESPONSE GUIDELINES
1. **Be Natural**: Write like you're texting a friend, not a formal email
2. **Be Concise**: WhatsApp has limits, keep responses short but helpful
3. **Be Proactive**: If you can guess what they need, offer it
4. **Be Contextual**: Use previous conversation to understand better
5. **Guide When Stuck**: If user needs help, show examples:
   - "Weather Delhi" for weather
   - "PNR 1234567890" for train booking
   - "Train 12301 status" for live status
   - "Restaurants near me" for local search
6. **Minimal Emojis**: One or two max, don't overdo it
7. **Match Their Energy**: Casual question = casual answer

## LANGUAGE INSTRUCTION
Respond in {language_name} ({language_code}). Use the appropriate script.
If Hindi/Hinglish:
- ALWAYS use polite form "आप" (aap), NEVER use informal "तुम" (tum) or "तू" (tu)
- Be respectful but warm - like talking to someone you respect
- Example: "आप कैसे हैं?" NOT "तुम कैसे हो?"
- Example: "आपको क्या चाहिए?" NOT "तुझे क्या चाहिए?"
- Mix Hindi-English naturally like educated Indians actually text

## CONTEXT CLUES
- Time of day: {time_of_day}
- Day: {day_of_week}
- If morning, can mention "good morning" naturally
- If late night, acknowledge they're up late if relevant

Remember: You're not a robot. You're a helpful friend who happens to know a lot!"""


SMART_FALLBACK_PROMPT = """You are a helpful WhatsApp assistant. Something went wrong while processing the user's request.

## WHAT HAPPENED
- User asked about: {original_intent}
- User's message: "{user_message}"
- Error type: {error_type}
- Error details: {error_details}

## YOUR TASK
1. Acknowledge the issue briefly (don't be overly apologetic)
2. If you can answer their question yourself, do it!
3. If you need more info, ask specifically what you need
4. Suggest alternatives if the service is down

## CONTEXT
{conversation_context}

## LANGUAGE
Respond in {language_name} ({language_code}).

## EXAMPLES OF GOOD RESPONSES

If train API is down:
"Train status service is having issues right now. You can check directly at enquiry.indianrail.gov.in. Want me to help with something else meanwhile?"

If weather failed due to missing city:
"Which city's weather do you want? Just tell me the name or share your location!"

If search failed:
"Couldn't find that. Can you be more specific? Like 'pizza places in Connaught Place' or share your location for nearby search."

Be helpful, not just apologetic!"""


ERROR_RECOVERY_STRATEGIES = {
    "weather": {
        "missing_location": "Which city's weather should I check? Or share your location for local weather!",
        "api_error": "Weather service is taking a break. Try again in a bit? Or ask me something else!",
    },
    "pnr_status": {
        "invalid_pnr": "That doesn't look like a valid PNR. PNR is a 10-digit number from your ticket. Example: PNR 1234567890",
        "api_error": "IRCTC is being slow. You can check at indianrail.gov.in/pnr_enquiry. What else can I help with?",
    },
    "train_status": {
        "invalid_train": "I need the train number (like 12301 for Rajdhani). Which train are you tracking?",
        "api_error": "Train tracking is down. Try enquiry.indianrail.gov.in or I can help with something else!",
    },
    "local_search": {
        "missing_location": "Share your location or tell me the area, and I'll find what you need!",
        "no_results": "Couldn't find that nearby. Try being more specific or a different area?",
    },
    "cricket_score": {
        "no_match": "No live match right now. Want yesterday's highlights or upcoming schedule?",
        "api_error": "Score service hiccup. Check cricbuzz.com for live updates. Anything else?",
    },
    "stock_price": {
        "invalid_symbol": "Which stock? Give me the name or symbol (like RELIANCE, TCS, INFY)",
        "api_error": "Stock data delayed. Check moneycontrol.com for live prices.",
    },
    "image": {
        "generation_failed": "Couldn't create that image. Try a simpler description? Like 'sunset on beach' or 'cute puppy'",
        "content_filter": "Can't generate that type of image. How about something different?",
    },
    "default": {
        "generic": "Hit a snag there. Could you rephrase or try something else?",
    }
}


def get_error_recovery(intent: str, error_type: str) -> str:
    """Get appropriate error recovery message."""
    intent_strategies = ERROR_RECOVERY_STRATEGIES.get(intent, ERROR_RECOVERY_STRATEGIES["default"])
    return intent_strategies.get(error_type, intent_strategies.get("generic", ERROR_RECOVERY_STRATEGIES["default"]["generic"]))


# =============================================================================
# SMART CHAT HANDLER
# =============================================================================

def get_time_context() -> Tuple[str, str]:
    """Get time-of-day context for natural responses."""
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


def get_language_info(lang_code: str) -> Tuple[str, str]:
    """Get language name and code."""
    lang_info = LANGUAGE_NAMES.get(lang_code, {"en": "English", "native": "English"})
    return lang_info.get("en", "English"), lang_code


async def smart_chat(state: BotState) -> dict:
    """
    Smart AI-powered chat handler with context awareness.

    Features:
    - Uses conversation memory
    - Adapts personality to language
    - Time-aware responses
    - Natural, human-like replies
    """
    user_message = (
        state.get("current_query", "")
        or state["whatsapp_message"].get("text", "")
    )

    phone = state["whatsapp_message"].get("from_number", "unknown")
    detected_lang = state.get("detected_language", "en")

    # Get conversation memory
    memory = ConversationMemory.get_or_create(phone)

    # Get language info
    language_name, language_code = get_language_info(detected_lang)

    # Get personality
    personality = get_personality(detected_lang)

    # Get time context
    time_of_day, day_of_week = get_time_context()

    # Build the prompt
    system_prompt = SMART_CHAT_SYSTEM_PROMPT.format(
        personality_style=personality["style"],
        conversation_context=memory.get_context_summary(),
        language_name=language_name,
        language_code=language_code,
        time_of_day=time_of_day,
        day_of_week=day_of_week
    )

    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.8,  # Slightly higher for more natural variation
            api_key=settings.OPENAI_API_KEY,
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        response = await llm.ainvoke(messages)
        response_text = response.content

        # Store in memory
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
            "intent": "chat",
        }

    except Exception as e:
        logger.error(f"Smart chat error: {e}")
        # Even error handling should be natural
        personality = get_personality(detected_lang)
        apology = personality["apology"][0] if personality.get("apology") else "Oops!"
        return {
            "response_text": f"{apology} Having a moment. Ask me again?",
            "response_type": "text",
            "should_fallback": False,
            "intent": "chat",
            "error": str(e)
        }


# Sync version for compatibility
def smart_chat_sync(state: BotState) -> dict:
    """Synchronous wrapper for smart_chat."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # If we're in an async context, we can't use run_until_complete
        # Fall back to the simple sync implementation
        return _smart_chat_sync_impl(state)

    return loop.run_until_complete(smart_chat(state))


def _smart_chat_sync_impl(state: BotState) -> dict:
    """Pure sync implementation of smart chat."""
    user_message = (
        state.get("current_query", "")
        or state["whatsapp_message"].get("text", "")
    )

    phone = state["whatsapp_message"].get("from_number", "unknown")
    detected_lang = state.get("detected_language", "en")

    # Get conversation memory
    memory = ConversationMemory.get_or_create(phone)

    # Get language info
    language_name, language_code = get_language_info(detected_lang)

    # Get personality
    personality = get_personality(detected_lang)

    # Get time context
    time_of_day, day_of_week = get_time_context()

    # Build the prompt
    system_prompt = SMART_CHAT_SYSTEM_PROMPT.format(
        personality_style=personality["style"],
        conversation_context=memory.get_context_summary(),
        language_name=language_name,
        language_code=language_code,
        time_of_day=time_of_day,
        day_of_week=day_of_week
    )

    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.8,
            api_key=settings.OPENAI_API_KEY,
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        response = llm.invoke(messages)
        response_text = response.content

        # Store in memory
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
            "intent": "chat",
        }

    except Exception as e:
        logger.error(f"Smart chat sync error: {e}")
        personality = get_personality(detected_lang)
        apology = personality["apology"][0] if personality.get("apology") else "Oops!"
        return {
            "response_text": f"{apology} Having a moment. Ask me again?",
            "response_type": "text",
            "should_fallback": False,
            "intent": "chat",
            "error": str(e)
        }


# =============================================================================
# SMART FALLBACK HANDLER
# =============================================================================

def smart_fallback(state: BotState) -> dict:
    """
    Intelligent fallback handler with context-aware error recovery.

    Features:
    - Analyzes what went wrong
    - Provides specific guidance based on intent
    - Offers alternatives
    - Uses AI for complex recovery
    """
    error = state.get("error", "")
    original_intent = state.get("intent", "unknown")
    user_message = state.get("current_query", "") or state["whatsapp_message"].get("text", "")
    phone = state["whatsapp_message"].get("from_number", "unknown")
    detected_lang = state.get("detected_language", "en")

    logger.warning(f"Smart fallback for intent '{original_intent}': {error}")

    # Get conversation memory
    memory = ConversationMemory.get_or_create(phone)

    # Analyze error type
    error_lower = error.lower() if error else ""

    # Determine error type
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

    # Try quick recovery first
    quick_recovery = get_error_recovery(original_intent, error_type)

    # Check if we can infer missing information
    if error_type == "missing_location" and original_intent in ["weather", "local_search"]:
        inferred_city = memory.infer_missing_entity(original_intent, "city")
        if inferred_city:
            quick_recovery = f"Did you mean {inferred_city}? Or tell me a different place!"

    # For simple errors, use quick recovery
    if error_type != "generic" and original_intent in ERROR_RECOVERY_STRATEGIES:
        # Translate if needed
        if detected_lang != "en":
            quick_recovery = _translate_quick(quick_recovery, detected_lang)

        return {
            "response_text": quick_recovery,
            "response_type": "text",
            "should_fallback": False,
            "intent": original_intent,
        }

    # For complex errors, use AI
    try:
        language_name, language_code = get_language_info(detected_lang)

        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )

        prompt = SMART_FALLBACK_PROMPT.format(
            original_intent=original_intent,
            user_message=user_message,
            error_type=error_type,
            error_details=error[:200] if error else "Unknown error",
            conversation_context=memory.get_context_summary(),
            language_name=language_name,
            language_code=language_code
        )

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Help me recover from this error for the user.")
        ])

        return {
            "response_text": response.content,
            "response_type": "text",
            "should_fallback": False,
            "intent": original_intent,
        }

    except Exception as e:
        logger.error(f"Smart fallback AI error: {e}")
        # Ultimate fallback - still be helpful
        personality = get_personality(detected_lang)
        apology = personality["apology"][0] if personality.get("apology") else "Oops!"

        return {
            "response_text": f"{apology} Let me try differently. What do you need help with?\n\nQuick options:\n• Weather - 'Weather Delhi'\n• Train - 'PNR 1234567890'\n• Search - 'Restaurants near me'",
            "response_type": "text",
            "should_fallback": False,
            "intent": "fallback",
        }


def _translate_quick(text: str, target_lang: str) -> str:
    """Quick translation for common phrases."""
    # For now, keep English for non-Hindi
    # Hindi translations for common phrases
    if target_lang == "hi":
        translations = {
            "Which city's weather should I check?": "किस शहर का मौसम बताऊं?",
            "share your location": "अपनी लोकेशन शेयर करो",
            "try again": "फिर से ट्राई करो",
            "What else can I help with?": "और क्या हेल्प करूं?",
        }
        for eng, hindi in translations.items():
            text = text.replace(eng, hindi)
    return text


# =============================================================================
# RESPONSE ENHANCER
# =============================================================================

def enhance_response(
    state: BotState,
    base_response: str,
    add_personality: bool = True,
    add_follow_up: bool = True
) -> str:
    """
    Enhance a basic response with personality and follow-ups.

    Use this to make API responses more human-like.
    """
    detected_lang = state.get("detected_language", "en")
    intent = state.get("intent", "unknown")
    personality = get_personality(detected_lang)

    enhanced = base_response

    # Add contextual follow-up suggestions
    if add_follow_up:
        follow_ups = get_contextual_follow_ups(intent, detected_lang)
        if follow_ups:
            enhanced += f"\n\n{follow_ups}"

    return enhanced


def get_contextual_follow_ups(intent: str, lang: str) -> str:
    """Get relevant follow-up suggestions based on intent."""
    follow_ups = {
        "weather": {
            "en": "Want tomorrow's forecast too?",
            "hi": "कल का मौसम भी बताऊं?"
        },
        "pnr_status": {
            "en": "Need train's live location?",
            "hi": "ट्रेन की लाइव लोकेशन चाहिए?"
        },
        "cricket_score": {
            "en": "Want match highlights or schedule?",
            "hi": "मैच हाइलाइट्स या शेड्यूल चाहिए?"
        },
        "stock_price": {
            "en": "Track another stock?",
            "hi": "कोई और स्टॉक देखना है?"
        },
        "get_horoscope": {
            "en": "Want weekly prediction too?",
            "hi": "हफ्ते का राशिफल भी बताऊं?"
        },
        "local_search": {
            "en": "Want more options or directions?",
            "hi": "और ऑप्शन या रास्ता बताऊं?"
        },
    }

    if intent in follow_ups:
        return follow_ups[intent].get(lang, follow_ups[intent].get("en", ""))
    return ""


# =============================================================================
# AI UNDERSTANDING (Used by intent detection)
# =============================================================================

async def ai_understand_query(
    message: str,
    context: Optional[str] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Use AI to deeply understand a user's query.

    Returns:
        dict with keys: intent, entities, sentiment, clarification_needed, suggested_response
    """
    prompt = f"""Analyze this WhatsApp message from an Indian user.

Message: "{message}"
{f'Context: {context}' if context else ''}

Determine:
1. Primary intent (what do they want?)
2. Key entities (names, numbers, places, dates)
3. Sentiment (happy, frustrated, neutral, confused)
4. Is clarification needed? What specifically?
5. If this is a follow-up to previous message, what's the connection?

Respond in JSON format:
{{
    "intent": "weather|pnr_status|train_status|local_search|cricket_score|stock_price|get_news|govt_jobs|get_horoscope|image|chat|help",
    "confidence": 0.0-1.0,
    "entities": {{"city": "", "pnr": "", "train_number": "", "stock": "", "zodiac": ""}},
    "sentiment": "positive|negative|neutral|confused",
    "needs_clarification": true/false,
    "clarification_question": "string if needed",
    "is_follow_up": true/false,
    "follow_up_context": "what previous topic this relates to"
}}"""

    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )

        response = llm.invoke([HumanMessage(content=prompt)])

        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

    except Exception as e:
        logger.error(f"AI understand error: {e}")

    return {
        "intent": "chat",
        "confidence": 0.5,
        "entities": {},
        "sentiment": "neutral",
        "needs_clarification": False
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ConversationMemory",
    "smart_chat",
    "smart_chat_sync",
    "smart_fallback",
    "enhance_response",
    "get_personality",
    "get_contextual_follow_ups",
    "ai_understand_query",
    "get_error_recovery",
]
