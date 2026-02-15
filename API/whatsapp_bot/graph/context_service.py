"""
Centralized Conversation Context Service

Provides:
- Conversation history storage (last N messages)
- Active topic and entity tracking
- Redis-based scalable storage with in-memory fallback
- TTL-based expiration
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
MAX_HISTORY_SIZE = 10  # Store last 10 messages
DEFAULT_TTL_SECONDS = 1800  # 30 minutes
REDIS_KEY_PREFIX = "whatsapp:conversation:"

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Try to get Redis URL from settings
try:
    from common.config.settings import settings
    REDIS_URL = getattr(settings, 'REDIS_URL', None)
except ImportError:
    REDIS_URL = None


@dataclass
class Message:
    """Represents a single message in conversation history."""
    role: str  # "user" or "bot"
    text: str
    timestamp: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(
            role=data.get("role", "user"),
            text=data.get("text", ""),
            timestamp=data.get("timestamp", ""),
            intent=data.get("intent"),
            entities=data.get("entities"),
        )


@dataclass
class ConversationContext:
    """Represents the full conversation context for a user."""
    phone: str
    messages: List[Message]
    active_topic: Optional[str] = None  # Current topic: "travel", "weather", "astrology", etc.
    active_entities: Optional[Dict[str, Any]] = None  # Entities relevant to active topic
    last_updated: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "phone": self.phone,
            "messages": [m.to_dict() for m in self.messages],
            "active_topic": self.active_topic,
            "active_entities": self.active_entities,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationContext":
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            phone=data.get("phone", ""),
            messages=messages,
            active_topic=data.get("active_topic"),
            active_entities=data.get("active_entities"),
            last_updated=data.get("last_updated", 0.0),
        )

    def get_last_user_message(self) -> Optional[Message]:
        """Get the most recent user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg
        return None

    def get_last_bot_message(self) -> Optional[Message]:
        """Get the most recent bot message."""
        for msg in reversed(self.messages):
            if msg.role == "bot":
                return msg
        return None

    def get_last_intent(self) -> Optional[str]:
        """Get the intent from the last user message."""
        last_user = self.get_last_user_message()
        return last_user.intent if last_user else None

    def get_last_entities(self) -> Optional[Dict]:
        """Get entities from the last user message."""
        last_user = self.get_last_user_message()
        return last_user.entities if last_user else None

    def get_history_text(self, max_messages: int = 5) -> str:
        """Get conversation history as formatted text for LLM context."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        lines = []
        for msg in recent:
            role_label = "User" if msg.role == "user" else "Bot"
            text_preview = msg.text[:200] + "..." if len(msg.text) > 200 else msg.text
            lines.append(f"{role_label}: {text_preview}")
        return "\n".join(lines)


class ConversationContextService:
    """
    Service for managing conversation context.

    Uses Redis for distributed storage with in-memory fallback.
    """

    def __init__(self):
        self._redis_client: Optional[Any] = None
        self._memory_store: Dict[str, Dict] = {}
        self._redis_checked = False
        self._use_redis = False  # Flag to track if Redis is available

    def _get_redis_client(self) -> Optional[Any]:
        """Lazily initialize Redis client."""
        if self._redis_checked:
            return self._redis_client if self._use_redis else None

        self._redis_checked = True

        if not REDIS_AVAILABLE or not REDIS_URL:
            logger.info("Redis not available, using in-memory storage for conversation context")
            self._use_redis = False
            return None

        try:
            self._redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            self._redis_client.ping()
            logger.info("Redis connected for conversation context")
            self._use_redis = True
            return self._redis_client
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory storage: {e}")
            self._use_redis = False
            return None

    def _redis_key(self, phone: str) -> str:
        """Generate Redis key for a phone number."""
        return f"{REDIS_KEY_PREFIX}{phone}"

    async def get_context(self, phone: str) -> Optional[ConversationContext]:
        """
        Get conversation context for a phone number.

        Args:
            phone: User's phone number

        Returns:
            ConversationContext if exists and not expired, None otherwise
        """
        if not phone:
            return None

        # Initialize Redis check
        self._get_redis_client()

        # Use Redis if available and working
        if self._use_redis and self._redis_client:
            try:
                data = self._redis_client.get(self._redis_key(phone))
                if data:
                    context_dict = json.loads(data)
                    return ConversationContext.from_dict(context_dict)
                return None
            except Exception as e:
                logger.warning(f"Redis get failed, falling back to memory: {e}")
                self._use_redis = False  # Disable Redis for future calls

        # In-memory storage (fallback or primary)
        if phone in self._memory_store:
            context_dict = self._memory_store[phone]
            # Check TTL
            if time.time() - context_dict.get("last_updated", 0) > DEFAULT_TTL_SECONDS:
                del self._memory_store[phone]
                return None
            return ConversationContext.from_dict(context_dict)

        return None

    async def save_context(self, context: ConversationContext) -> bool:
        """
        Save conversation context.

        Args:
            context: ConversationContext to save

        Returns:
            True if saved successfully
        """
        if not context.phone:
            return False

        context.last_updated = time.time()
        context_dict = context.to_dict()

        # Initialize Redis check
        self._get_redis_client()

        # Try Redis if available
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.setex(
                    self._redis_key(context.phone),
                    DEFAULT_TTL_SECONDS,
                    json.dumps(context_dict)
                )
                return True
            except Exception as e:
                logger.warning(f"Redis save failed, falling back to memory: {e}")
                self._use_redis = False  # Disable Redis for future calls

        # In-memory storage (fallback or primary)
        self._memory_store[context.phone] = context_dict
        return True

    async def add_user_message(
        self,
        phone: str,
        text: str,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
    ) -> ConversationContext:
        """
        Add a user message to conversation history.

        Args:
            phone: User's phone number
            text: Message text
            intent: Detected intent
            entities: Extracted entities

        Returns:
            Updated ConversationContext
        """
        context = await self.get_context(phone)

        if not context:
            context = ConversationContext(
                phone=phone,
                messages=[],
                active_topic=None,
                active_entities=None,
            )

        # Create new message
        message = Message(
            role="user",
            text=text,
            timestamp=datetime.now().isoformat(),
            intent=intent,
            entities=entities,
        )

        # Add to history
        context.messages.append(message)

        # Trim to max size
        if len(context.messages) > MAX_HISTORY_SIZE:
            context.messages = context.messages[-MAX_HISTORY_SIZE:]

        # Update active topic and entities based on intent
        if intent and intent not in ["chat", "unknown", "clarification_needed"]:
            context.active_topic = self._intent_to_topic(intent)
            if entities:
                context.active_entities = entities

        # Save
        await self.save_context(context)

        return context

    async def add_bot_message(
        self,
        phone: str,
        text: str,
    ) -> ConversationContext:
        """
        Add a bot response to conversation history.

        Args:
            phone: User's phone number
            text: Response text

        Returns:
            Updated ConversationContext
        """
        context = await self.get_context(phone)

        if not context:
            context = ConversationContext(
                phone=phone,
                messages=[],
            )

        # Create new message
        message = Message(
            role="bot",
            text=text[:500],  # Truncate long responses
            timestamp=datetime.now().isoformat(),
        )

        # Add to history
        context.messages.append(message)

        # Trim to max size
        if len(context.messages) > MAX_HISTORY_SIZE:
            context.messages = context.messages[-MAX_HISTORY_SIZE:]

        # Save
        await self.save_context(context)

        return context

    async def update_active_context(
        self,
        phone: str,
        topic: Optional[str] = None,
        entities: Optional[Dict] = None,
    ) -> bool:
        """
        Update the active topic and entities without adding a message.

        Args:
            phone: User's phone number
            topic: Active topic
            entities: Active entities

        Returns:
            True if updated successfully
        """
        context = await self.get_context(phone)

        if not context:
            return False

        if topic:
            context.active_topic = topic
        if entities:
            # Merge entities instead of replacing
            if context.active_entities:
                context.active_entities.update(entities)
            else:
                context.active_entities = entities

        return await self.save_context(context)

    async def clear_context(self, phone: str) -> bool:
        """
        Clear conversation context for a phone number.

        Args:
            phone: User's phone number

        Returns:
            True if cleared successfully
        """
        if not phone:
            return False

        # Initialize Redis check
        self._get_redis_client()

        # Try Redis if available
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.delete(self._redis_key(phone))
                # Also clear from memory in case it was stored there
                self._memory_store.pop(phone, None)
                return True
            except Exception as e:
                logger.warning(f"Redis clear failed, falling back to memory: {e}")
                self._use_redis = False

        # In-memory storage (fallback or primary)
        self._memory_store.pop(phone, None)
        return True

    def _intent_to_topic(self, intent: str) -> str:
        """Map intent to a topic category."""
        topic_map = {
            # Travel
            "train_journey": "travel",
            "train_status": "travel",
            "pnr_status": "travel",
            "metro_ticket": "travel",
            # Weather
            "weather": "weather",
            # Astrology
            "get_horoscope": "astrology",
            "birth_chart": "astrology",
            "kundli_matching": "astrology",
            "dosha": "astrology",
            "life_prediction": "astrology",
            "numerology": "astrology",
            "tarot_reading": "astrology",
            # News & Info
            "get_news": "news",
            "cricket_score": "sports",
            "stock_price": "finance",
            # Jobs & Schemes
            "govt_jobs": "jobs",
            "govt_schemes": "schemes",
            "farmer_schemes": "schemes",
            # Local
            "local_search": "local",
            "food_order": "food",
            "events": "events",
            # Utilities
            "image": "image",
            "image_analysis": "image",
            "set_reminder": "reminder",
        }
        return topic_map.get(intent, "general")


# Singleton instance
_context_service: Optional[ConversationContextService] = None


def get_context_service() -> ConversationContextService:
    """Get or create the singleton context service instance."""
    global _context_service
    if _context_service is None:
        _context_service = ConversationContextService()
    return _context_service
