"""Conversation history and context management."""

import time
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)
    intent: str = ""
    metadata: dict = field(default_factory=dict)


class ConversationManager:
    """Manages conversation history per session with automatic cleanup."""

    def __init__(self, max_history: int = 10, session_timeout_minutes: int = 30):
        self._sessions: dict[str, list[Message]] = {}
        self._last_activity: dict[str, float] = {}
        self._max_history = max_history
        self._timeout = session_timeout_minutes * 60

    def add_message(self, session_id: str, role: str, content: str, intent: str = "", metadata: dict | None = None):
        """Add a message to a session's history."""
        self._cleanup_expired()

        if session_id not in self._sessions:
            self._sessions[session_id] = []

        msg = Message(
            role=role,
            content=content,
            intent=intent,
            metadata=metadata or {},
        )
        self._sessions[session_id].append(msg)
        self._last_activity[session_id] = time.time()

        # Trim to max history
        if len(self._sessions[session_id]) > self._max_history:
            self._sessions[session_id] = self._sessions[session_id][-self._max_history:]

    def get_history(self, session_id: str) -> list[Message]:
        """Get conversation history for a session."""
        self._cleanup_expired()
        return self._sessions.get(session_id, [])

    def get_context_messages(self, session_id: str) -> list[dict[str, str]]:
        """Get history formatted for LLM context (list of role/content dicts)."""
        history = self.get_history(session_id)
        return [{"role": m.role, "content": m.content} for m in history]

    def clear_session(self, session_id: str):
        """Clear a session's history."""
        self._sessions.pop(session_id, None)
        self._last_activity.pop(session_id, None)

    def active_sessions_count(self) -> int:
        """Return the number of active sessions."""
        self._cleanup_expired()
        return len(self._sessions)

    def _cleanup_expired(self):
        """Remove sessions that have been inactive beyond the timeout."""
        now = time.time()
        expired = [
            sid for sid, last in self._last_activity.items()
            if now - last > self._timeout
        ]
        for sid in expired:
            self._sessions.pop(sid, None)
            self._last_activity.pop(sid, None)
