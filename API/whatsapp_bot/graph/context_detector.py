"""
Smart Context Detector

Hybrid approach:
1. Fast pattern matching for obvious cases (85% of messages)
2. AI-powered understanding for ambiguous cases (15% of messages)

Determines:
- Is this a follow-up to previous conversation?
- Should we reuse context (entities, topic)?
- What type of follow-up is it? (continuation, modification, clarification, new_topic)
"""

import logging
import re
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from whatsapp_bot.graph.context_service import ConversationContext, get_context_service

logger = logging.getLogger(__name__)

# Try to get OpenAI key
try:
    from common.config.settings import settings
    OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)
except ImportError:
    OPENAI_API_KEY = None


class ContextType(str, Enum):
    """Type of context relationship with previous conversation."""
    CONTINUATION = "continuation"      # Same topic, following up (e.g., "aur batao")
    MODIFICATION = "modification"      # Same topic, changing parameters (e.g., "car se batao")
    CLARIFICATION = "clarification"    # Answering bot's question (e.g., "delhi" after "which city?")
    NEW_TOPIC = "new_topic"            # Starting fresh conversation


@dataclass
class ContextDecision:
    """Decision about how to handle context for current message."""
    use_context: bool                  # Should we use previous context?
    context_type: ContextType          # Type of context relationship
    entities_to_reuse: Dict[str, Any]  # Entities to carry forward
    confidence: float                  # Confidence in this decision
    reason: str                        # Explanation for debugging


class EntityModifications(BaseModel):
    """Explicit entity modifications for structured output compatibility."""
    travel_mode: Optional[str] = Field(None, description="Travel mode change: 'car', 'train', 'bus', 'flight', or None")
    is_road_trip: bool = Field(False, description="Whether this is a road trip request")
    city_change: Optional[str] = Field(None, description="New city if changing, else None")
    date_change: Optional[str] = Field(None, description="New date if changing, else None")

    class Config:
        extra = "forbid"


class AIContextUnderstanding(BaseModel):
    """Structured output from AI context understanding."""
    is_followup: bool = Field(description="Is this message a follow-up to the previous conversation?")
    context_type: str = Field(description="Type: 'continuation', 'modification', 'clarification', or 'new_topic'")
    reuse_entities: bool = Field(description="Should we reuse entities (like cities, dates) from previous context?")
    modifications: EntityModifications = Field(
        default_factory=EntityModifications,
        description="Specific entity modifications"
    )
    confidence: float = Field(description="Confidence score 0-1")
    reason: str = Field(description="Brief explanation of the decision")

    class Config:
        extra = "forbid"


# Pattern definitions for fast matching
CLEAR_NEW_INTENT_PATTERNS = {
    # Weather with city
    "weather": [
        r"weather\s+(?:in|of|at)\s+\w+",
        r"\w+\s+weather\b",  # "delhi weather", "mumbai weather"
        r"\w+\s+(?:ka|ki|का|की)\s+(?:mausam|weather|मौसम)",
        r"(?:mausam|weather|मौसम)\s+(?:in|of|at|में)\s+\w+",
        r"\w+\s+(?:ka|ki|का|की)\s+(?:mausam|मौसम)",  # "delhi ka mausam"
    ],
    # Train with number
    "train_status": [
        r"train\s+\d{5}",
        r"\d{5}\s+(?:train|status)",
        r"(?:ट्रेन|train)\s+(?:number|no\.?|नंबर)\s*\d{5}",
    ],
    # PNR
    "pnr_status": [
        r"pnr\s+\d{10}",
        r"\d{10}",
    ],
    # Travel with cities
    "train_journey": [
        r"(?:from|se|से)\s+\w+\s+(?:to|tak|तक|को)\s+\w+",
        r"\w+\s+(?:se|से)\s+\w+\s+(?:travel|trip|journey|yatra|यात्रा)",
    ],
    # Cricket
    "cricket_score": [
        r"(?:cricket|ipl|match)\s+(?:score|result)",
        r"(?:score|result)\s+(?:cricket|ipl|match)",
    ],
    # News with topic
    "get_news": [
        r"(?:news|khabar|खबर)\s+(?:about|on|of)\s+\w+",
        r"\w+\s+(?:news|khabar|खबर)",
    ],
}

# Patterns that indicate follow-up
FOLLOWUP_PATTERNS = {
    # Continuation patterns
    "continuation": [
        r"^(?:aur|और|more|next|aage|आगे)\b",
        r"^(?:tell me more|aur batao|और बताओ)\b",
        r"^(?:details|विवरण)\b",
        r"^(?:what else|kya aur|क्या और)\b",
    ],
    # Modification patterns (travel specific)
    "travel_modification": [
        r"(?:car|गाड़ी|gaadi|drive|कार)\s+(?:se|से|wala|वाला|travel|trip)",
        r"(?:by|via)\s+(?:car|train|bus|flight|plane)",
        r"(?:train|ट्रेन|rail|रेल)\s+(?:se|से|wala|वाला)",
        r"(?:bus|बस)\s+(?:se|से|wala|वाला)",
        r"(?:flight|फ्लाइट|plane|हवाई)\s+(?:se|से|wala|वाला)",
        r"(?:road\s*trip|रोड\s*ट्रिप)",
    ],
    # Time modification
    "time_modification": [
        r"(?:tomorrow|kal|कल|parso|परसों)\s*(?:ka|की|के)?",
        r"(?:today|aaj|आज)\s*(?:ka|की|के)?",
        r"(?:next\s+week|agle\s+hafte)",
        r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
    ],
    # General modification
    "general_modification": [
        r"(?:same|wahi|वही)\s+(?:but|lekin|लेकिन|par|पर)",
        r"(?:instead|jagah|जगह)\s+(?:of|pe|पे)",
        r"(?:change|badal|बदल)\s+(?:kar|करो|do|दो)",
    ],
    # Local search location change patterns
    "local_search_modification": [
        r"^(?:near|in|at)\s+\w+",  # "near hajipur", "in delhi"
        r"^(?:के पास|में|पास)\s+\w+",  # Hindi: "के पास", "में"
        r"^\w+\s+(?:ke\s+pass|ke\s+paas|में|mein|me)\b",  # "hajipur ke pass"
        r"^(?:what about|aur)\s+(?:near|in|at)?\s*\w+",  # "what about in delhi"
    ],
}

# Patterns that clearly indicate new topic
NEW_TOPIC_INDICATORS = [
    r"^(?:ok|okay|theek|ठीक|accha|अच्छा)[\s,]+(?:now|ab|अब)",
    r"^(?:btw|by the way|waise|वैसे)",
    r"^(?:something else|kuch aur|कुछ और)",
    r"^(?:new|naya|नया)\s+(?:question|sawal|सवाल)",
    r"^(?:forget|chhodo|छोड़ो)\s+(?:that|wo|वो)",
]


class SmartContextDetector:
    """
    Hybrid context detector using pattern matching + AI.
    """

    def __init__(self):
        self._llm = None

    def _get_llm(self):
        """Lazily initialize LLM."""
        if self._llm is None and OPENAI_API_KEY:
            self._llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=OPENAI_API_KEY,
                max_tokens=300,
            ).with_structured_output(AIContextUnderstanding)
        return self._llm

    async def detect_context(
        self,
        current_message: str,
        context: Optional[ConversationContext],
        detected_lang: str = "en",
    ) -> ContextDecision:
        """
        Detect context relationship for current message.

        Args:
            current_message: The current user message
            context: Previous conversation context
            detected_lang: Detected language of message

        Returns:
            ContextDecision with instructions on how to handle context
        """
        message_lower = current_message.lower().strip()

        # No previous context - everything is new
        if not context or not context.messages:
            return ContextDecision(
                use_context=False,
                context_type=ContextType.NEW_TOPIC,
                entities_to_reuse={},
                confidence=1.0,
                reason="No previous context exists",
            )

        # Step 1: Check for clear new intent (fast pattern match)
        new_intent = self._check_clear_new_intent(message_lower)
        if new_intent:
            return ContextDecision(
                use_context=False,
                context_type=ContextType.NEW_TOPIC,
                entities_to_reuse={},
                confidence=0.95,
                reason=f"Clear new intent detected: {new_intent}",
            )

        # Step 2: Check for explicit new topic indicators
        if self._is_new_topic_indicator(message_lower):
            return ContextDecision(
                use_context=False,
                context_type=ContextType.NEW_TOPIC,
                entities_to_reuse={},
                confidence=0.9,
                reason="Explicit new topic indicator found",
            )

        # Step 3: Check for obvious follow-up patterns
        followup_result = self._check_followup_patterns(message_lower, context)
        if followup_result:
            return followup_result

        # Step 4: Check message length and context hints
        quick_decision = self._quick_context_check(message_lower, context)
        if quick_decision and quick_decision.confidence >= 0.8:
            return quick_decision

        # Step 5: Ambiguous case - use AI (only ~15% of messages reach here)
        ai_decision = await self._ai_understand_context(current_message, context, detected_lang)
        if ai_decision:
            return ai_decision

        # Step 6: Fallback - if message is short and we have context, assume follow-up
        if len(message_lower.split()) <= 4 and context.active_entities:
            return ContextDecision(
                use_context=True,
                context_type=ContextType.CONTINUATION,
                entities_to_reuse=context.active_entities or {},
                confidence=0.6,
                reason="Short message with active context - assuming follow-up",
            )

        # Default: treat as new topic
        return ContextDecision(
            use_context=False,
            context_type=ContextType.NEW_TOPIC,
            entities_to_reuse={},
            confidence=0.5,
            reason="Unable to determine context relationship - treating as new",
        )

    def _check_clear_new_intent(self, message: str) -> Optional[str]:
        """Check if message clearly indicates a new intent with complete info."""
        for intent, patterns in CLEAR_NEW_INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    # Additional check: make sure it's not just a modifier
                    # e.g., "by train" alone shouldn't trigger train_journey
                    if intent == "train_journey":
                        # Need both source and destination
                        if not re.search(r"\w+\s+(?:se|से|to|from)\s+\w+", message, re.IGNORECASE):
                            continue
                    return intent
        return None

    def _is_new_topic_indicator(self, message: str) -> bool:
        """Check if message has explicit new topic indicators."""
        for pattern in NEW_TOPIC_INDICATORS:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def _check_followup_patterns(
        self,
        message: str,
        context: ConversationContext,
    ) -> Optional[ContextDecision]:
        """Check for obvious follow-up patterns."""
        last_intent = context.get_last_intent()
        active_entities = context.active_entities or {}

        # Check continuation patterns
        for pattern in FOLLOWUP_PATTERNS["continuation"]:
            if re.search(pattern, message, re.IGNORECASE):
                return ContextDecision(
                    use_context=True,
                    context_type=ContextType.CONTINUATION,
                    entities_to_reuse=active_entities,
                    confidence=0.9,
                    reason="Continuation keyword detected",
                )

        # Check travel modification patterns (if last intent was travel-related)
        if last_intent in ["train_journey", "train_status"]:
            for pattern in FOLLOWUP_PATTERNS["travel_modification"]:
                if re.search(pattern, message, re.IGNORECASE):
                    # Determine the travel mode being requested
                    mode_entities = self._extract_travel_mode(message)
                    merged_entities = {**active_entities, **mode_entities}
                    return ContextDecision(
                        use_context=True,
                        context_type=ContextType.MODIFICATION,
                        entities_to_reuse=merged_entities,
                        confidence=0.95,
                        reason=f"Travel mode modification detected: {mode_entities}",
                    )

        # Check time modification patterns
        for pattern in FOLLOWUP_PATTERNS["time_modification"]:
            if re.search(pattern, message, re.IGNORECASE):
                if context.active_topic and active_entities:
                    return ContextDecision(
                        use_context=True,
                        context_type=ContextType.MODIFICATION,
                        entities_to_reuse=active_entities,
                        confidence=0.85,
                        reason="Time modification detected",
                    )

        # Check general modification patterns
        for pattern in FOLLOWUP_PATTERNS["general_modification"]:
            if re.search(pattern, message, re.IGNORECASE):
                if active_entities:
                    return ContextDecision(
                        use_context=True,
                        context_type=ContextType.MODIFICATION,
                        entities_to_reuse=active_entities,
                        confidence=0.8,
                        reason="General modification pattern detected",
                    )

        # Check local_search location modification patterns
        if last_intent == "local_search":
            for pattern in FOLLOWUP_PATTERNS["local_search_modification"]:
                if re.search(pattern, message, re.IGNORECASE):
                    # Extract the new location from message
                    new_location = self._extract_location_from_message(message)
                    if new_location and active_entities:
                        # Keep the search_query, update the location
                        merged_entities = active_entities.copy()
                        merged_entities["location"] = new_location
                        merged_entities["location_changed"] = True
                        return ContextDecision(
                            use_context=True,
                            context_type=ContextType.MODIFICATION,
                            entities_to_reuse=merged_entities,
                            confidence=0.9,
                            reason=f"Local search location changed to: {new_location}",
                        )

        return None

    def _extract_location_from_message(self, message: str) -> Optional[str]:
        """Extract location from a local search follow-up message."""
        message_lower = message.lower().strip()

        # Patterns to extract location
        patterns = [
            r"^(?:near|in|at)\s+(.+)$",  # "near hajipur vaishali"
            r"^(?:के पास|में|पास)\s+(.+)$",  # Hindi
            r"^(.+)\s+(?:ke\s+pass|ke\s+paas|में|mein|me)$",  # "hajipur ke pass"
            r"^(?:what about|aur)\s+(?:near|in|at)?\s*(.+)$",  # "what about delhi"
        ]

        for pattern in patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up the location
                location = re.sub(r"\s+", " ", location)
                if location and len(location) > 1:
                    return location.title()

        # If no pattern matched, but message is short (likely just a location)
        if len(message_lower.split()) <= 4 and not any(
            kw in message_lower for kw in ["what", "how", "when", "why", "which"]
        ):
            return message_lower.title()

        return None

    def _extract_travel_mode(self, message: str) -> Dict[str, Any]:
        """Extract travel mode from message."""
        message_lower = message.lower()

        mode_patterns = {
            "road_trip": [
                r"(?:car|गाड़ी|gaadi|drive|कार|driving|by\s*car|car\s*se|कार\s*से)",
                r"(?:road\s*trip|रोड\s*ट्रिप|self\s*drive)",
            ],
            "train_only": [
                r"(?:train|ट्रेन|rail|रेल|railway)",
            ],
            "flight_only": [
                r"(?:flight|फ्लाइट|plane|हवाई|fly|air)",
            ],
            "bus_only": [
                r"(?:bus|बस|volvo|sleeper)",
            ],
        }

        for mode, patterns in mode_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    if mode == "road_trip":
                        return {"road_trip": True, "multi_mode": False}
                    elif mode == "train_only":
                        return {"train_only": True, "multi_mode": False}
                    elif mode == "flight_only":
                        return {"flight_only": True, "multi_mode": False}
                    elif mode == "bus_only":
                        return {"bus_only": True, "multi_mode": False}

        return {}

    def _quick_context_check(
        self,
        message: str,
        context: ConversationContext,
    ) -> Optional[ContextDecision]:
        """Quick heuristic-based context check."""
        words = message.split()
        word_count = len(words)

        # Very short messages (1-2 words) with active context are likely follow-ups
        if word_count <= 2 and context.active_entities:
            # But check if it's a greeting or command
            greetings = {"hi", "hello", "hey", "bye", "thanks", "ok", "okay", "haan", "nahi", "yes", "no"}
            if words[0].lower() in greetings:
                return None

            return ContextDecision(
                use_context=True,
                context_type=ContextType.CONTINUATION,
                entities_to_reuse=context.active_entities,
                confidence=0.8,
                reason="Very short message with active context",
            )

        # Messages with pronouns referring to previous context
        referential_words = {"it", "this", "that", "same", "wahi", "वही", "isi", "इसी", "uska", "उसका"}
        if any(word.lower() in referential_words for word in words):
            if context.active_entities:
                return ContextDecision(
                    use_context=True,
                    context_type=ContextType.CONTINUATION,
                    entities_to_reuse=context.active_entities,
                    confidence=0.85,
                    reason="Referential word detected",
                )

        return None

    async def _ai_understand_context(
        self,
        current_message: str,
        context: ConversationContext,
        detected_lang: str,
    ) -> Optional[ContextDecision]:
        """Use AI to understand context when pattern matching is insufficient."""
        llm = self._get_llm()
        if not llm:
            return None

        try:
            # Build conversation history for AI
            history_text = context.get_history_text(max_messages=4)
            active_topic = context.active_topic or "unknown"
            active_entities = context.active_entities or {}

            prompt = f"""Analyze if the current message is a follow-up to the previous conversation.

CONVERSATION HISTORY:
{history_text}

ACTIVE TOPIC: {active_topic}
ACTIVE ENTITIES: {active_entities}

CURRENT MESSAGE: "{current_message}"

Determine:
1. Is this a follow-up to the previous conversation?
2. If follow-up, what type?
   - "continuation": Asking for more info on same topic (e.g., "aur batao", "tell me more")
   - "modification": Same topic but changing a parameter (e.g., "by car instead", "tomorrow instead")
   - "clarification": Answering a question the bot asked
   - "new_topic": Starting a completely new conversation

3. Should we reuse the active entities (like cities, dates)?

Examples:
- After showing Delhi-Mumbai travel options, "car wala batao" → modification, reuse cities
- After weather shown, "and humidity?" → continuation, reuse city
- After travel plan, "cricket score batao" → new_topic, don't reuse
- After "which city?", user says "delhi" → clarification

Respond in the user's language context: {detected_lang}"""

            result = await llm.ainvoke(prompt)

            # Map AI result to ContextDecision
            context_type_map = {
                "continuation": ContextType.CONTINUATION,
                "modification": ContextType.MODIFICATION,
                "clarification": ContextType.CLARIFICATION,
                "new_topic": ContextType.NEW_TOPIC,
            }

            context_type = context_type_map.get(result.context_type, ContextType.NEW_TOPIC)

            # Determine entities to reuse
            entities_to_reuse = {}
            if result.reuse_entities and context.active_entities:
                entities_to_reuse = context.active_entities.copy()

            # Apply modifications from structured output
            if result.modifications:
                mods = result.modifications
                if mods.travel_mode:
                    mode_map = {
                        "car": {"road_trip": True, "multi_mode": False},
                        "train": {"train_only": True, "multi_mode": False},
                        "bus": {"bus_only": True, "multi_mode": False},
                        "flight": {"flight_only": True, "multi_mode": False},
                    }
                    if mods.travel_mode in mode_map:
                        entities_to_reuse.update(mode_map[mods.travel_mode])
                if mods.is_road_trip:
                    entities_to_reuse["road_trip"] = True
                    entities_to_reuse["multi_mode"] = False
                if mods.city_change:
                    entities_to_reuse["city"] = mods.city_change
                if mods.date_change:
                    entities_to_reuse["travel_date"] = mods.date_change

            return ContextDecision(
                use_context=result.is_followup,
                context_type=context_type,
                entities_to_reuse=entities_to_reuse,
                confidence=result.confidence,
                reason=f"AI: {result.reason}",
            )

        except Exception as e:
            logger.warning(f"AI context understanding failed: {e}")
            return None


# Singleton instance
_context_detector: Optional[SmartContextDetector] = None


def get_context_detector() -> SmartContextDetector:
    """Get or create the singleton context detector instance."""
    global _context_detector
    if _context_detector is None:
        _context_detector = SmartContextDetector()
    return _context_detector
