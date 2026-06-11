"""
SignBridge AI — Layer 5: Context Manager
Maintains a sliding window of recent translations to enable
context-aware grammar correction and conversational coherence.
"""

import uuid
from datetime import UTC, datetime

from config.logger import setup_logger
from translation.schemas import ContextEntry, ContextWindow

logger = setup_logger("translation.context_manager")

# Maximum context window size
DEFAULT_WINDOW_SIZE = 10


class TranslationContextManager:
    """
    Manages per-session conversation context for the Translation Engine.

    Maintains a sliding window of recent sign-to-text translation turns.
    Provides context hints to the grammar fixer and providers to produce
    more coherent, conversation-aware translations.

    Example:
        Turn 1: [WATER, WANT] → "I would like some water."
        Turn 2: [PLEASE, HURRY] → With context: "Please hurry with the water."
    """

    def __init__(self, max_turns: int = DEFAULT_WINDOW_SIZE):
        self._sessions: dict[str, ContextWindow] = {}
        self._max_turns = max_turns
        logger.info(f"ContextManager initialized (window={max_turns} turns)")

    def create_session(self) -> str:
        """
        Create a new translation session.

        Returns:
            Unique session ID string
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = ContextWindow(
            entries=[], max_turns=self._max_turns, session_id=session_id
        )
        logger.debug(f"Created translation session: {session_id}")
        return session_id

    def get_or_create_session(self, session_id: str | None) -> str:
        """
        Return existing session ID or create a new one if not found.

        Args:
            session_id: Existing session ID or None

        Returns:
            Valid session ID
        """
        if session_id and session_id in self._sessions:
            return session_id
        return self.create_session()

    def add_turn(
        self, session_id: str, signs: list[str], translation: str, language: str
    ) -> None:
        """
        Add a completed translation turn to the context window.

        Args:
            session_id: Active session ID
            signs: Sign tokens for this turn
            translation: Final translated text for this turn
            language: Target language used for this turn
        """
        if session_id not in self._sessions:
            logger.warning(f"Session {session_id} not found. Creating new session.")
            self._sessions[session_id] = ContextWindow(
                entries=[], max_turns=self._max_turns, session_id=session_id
            )

        window = self._sessions[session_id]
        turn_index = len(window.entries)

        entry = ContextEntry(
            signs=signs,
            translation=translation,
            language=language,
            turn_index=turn_index,
            timestamp=datetime.now(UTC).isoformat(),
        )

        window.entries.append(entry)

        # Enforce sliding window limit
        if len(window.entries) > window.max_turns:
            window.entries = window.entries[-window.max_turns :]

        logger.debug(
            f"Context turn {turn_index} added for session {session_id}: '{translation}'"
        )

    def get_context_strings(self, session_id: str) -> list[str]:
        """
        Retrieve recent translations as plain strings for grammar context injection.

        Args:
            session_id: Active session ID

        Returns:
            List of recent English translation strings (most recent last)
        """
        if session_id not in self._sessions:
            return []
        return [entry.translation for entry in self._sessions[session_id].entries]

    def get_recent_signs(self, session_id: str, n: int = 3) -> list[list[str]]:
        """
        Retrieve the last N sign sequences from context.

        Args:
            session_id: Active session ID
            n: Number of recent turns to retrieve

        Returns:
            List of sign token lists (most recent last)
        """
        if session_id not in self._sessions:
            return []
        entries = self._sessions[session_id].entries[-n:]
        return [entry.signs for entry in entries]

    def get_turn_count(self, session_id: str) -> int:
        """Return the number of turns in a session's context window."""
        if session_id not in self._sessions:
            return 0
        return len(self._sessions[session_id].entries)

    def clear_session(self, session_id: str) -> bool:
        """
        Clear all context entries for a session without deleting the session.

        Args:
            session_id: Session to clear

        Returns:
            True if session was found and cleared, False otherwise
        """
        if session_id in self._sessions:
            self._sessions[session_id].entries = []
            logger.info(f"Context cleared for session {session_id}")
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Permanently remove a session and all its context.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session {session_id} deleted.")
            return True
        return False

    def get_session_summary(self, session_id: str) -> dict:
        """
        Return a summary dict of a session's context state.

        Args:
            session_id: Session to summarize

        Returns:
            Dict with turn_count, languages_used, recent_translations
        """
        if session_id not in self._sessions:
            return {
                "session_id": session_id,
                "turn_count": 0,
                "languages_used": [],
                "recent_translations": [],
            }

        window = self._sessions[session_id]
        languages = list({e.language for e in window.entries})
        recent = [e.translation for e in window.entries[-5:]]

        return {
            "session_id": session_id,
            "turn_count": len(window.entries),
            "languages_used": languages,
            "recent_translations": recent,
        }


context_manager = TranslationContextManager()
