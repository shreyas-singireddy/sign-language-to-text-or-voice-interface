"""
SignBridge AI — Layer 7: Dialogue Manager
Orchestrates the full conversation flow, managing multiple sessions,
routing signer inputs through translation, and coordinating responses.
"""
import uuid
from typing import Dict, Optional, List

from conversation.session import ConversationSession
from conversation.schemas import DialogueTurn, SessionSummary, Message
from config.logger import setup_logger

logger = setup_logger("conversation.dialogue_manager")


class DialogueManager:
    """
    Layer 7 Dialogue Manager.
    Manages multiple concurrent conversation sessions and
    orchestrates the full sign→translate→context→respond pipeline.

    Usage in Streamlit:
        # Start session
        session_id = dialogue_manager.start_session(language="Spanish")

        # Process each signer turn
        turn = dialogue_manager.process_turn(
            session_id=session_id,
            signs=["WATER", "WANT"],
            translated_text="I would like some water.",
            language="Spanish",
            confidence=0.95
        )

        # Add listener reply
        dialogue_manager.add_listener_reply(session_id, "I'll get you some water right away!")

        # Get all messages for display
        messages = dialogue_manager.get_messages(session_id)
    """

    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}
        logger.info("DialogueManager initialized.")

    def start_session(self, language: str = "English") -> str:
        """
        Start a new conversation session.

        Args:
            language: Primary language for this conversation

        Returns:
            New unique session ID
        """
        session = ConversationSession(language=language)
        self._sessions[session.session_id] = session
        logger.info(f"New conversation session started: {session.session_id} ({language})")
        return session.session_id

    def get_or_create_session(self, session_id: Optional[str], language: str = "English") -> str:
        """
        Return an existing session or create a new one.

        Args:
            session_id: Existing session ID or None
            language: Language to use if creating a new session

        Returns:
            Valid session ID
        """
        if session_id and session_id in self._sessions:
            return session_id
        return self.start_session(language)

    def process_turn(
        self,
        session_id: str,
        signs: List[str],
        translated_text: str,
        language: str = "English",
        confidence: float = 1.0,
    ) -> DialogueTurn:
        """
        Process a complete signer turn and return the turn result.

        Args:
            session_id: Active session ID
            signs: Recognized sign tokens from Layer 4
            translated_text: Layer 5 translated text
            language: Target language
            confidence: Translation confidence

        Returns:
            DialogueTurn with emotion, suggestion, and metadata
        """
        session = self._get_session(session_id)
        return session.process_signer_input(
            signs=signs,
            translated_text=translated_text,
            language=language,
            confidence=confidence,
        )

    def add_listener_reply(self, session_id: str, text: str, language: str = "English") -> Message:
        """
        Add a reply from the hearing participant to the session.

        Args:
            session_id: Active session ID
            text: Listener's typed response
            language: Language of the response

        Returns:
            Created Message object
        """
        session = self._get_session(session_id)
        return session.add_listener_reply(text=text, language=language)

    def get_messages(self, session_id: str) -> List[Message]:
        """
        Retrieve all messages for a session.

        Args:
            session_id: Session to retrieve messages for

        Returns:
            All messages in chronological order
        """
        session = self._get_session(session_id)
        return session.get_all_messages()

    def get_recent_context(self, session_id: str, n: int = 5) -> List[str]:
        """
        Get recent translation strings for context-aware grammar engine.

        Args:
            session_id: Active session ID
            n: Number of recent turns

        Returns:
            List of recent English translations
        """
        session = self._get_session(session_id)
        return session.get_recent_context(n)

    def get_session_summary(self, session_id: str) -> SessionSummary:
        """
        Get a statistics summary for a session.

        Args:
            session_id: Session to summarize

        Returns:
            SessionSummary object
        """
        session = self._get_session(session_id)
        return session.get_summary()

    def reset_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session.

        Args:
            session_id: Session to reset

        Returns:
            True if reset successfully
        """
        if session_id in self._sessions:
            self._sessions[session_id].reset()
            logger.info(f"Session {session_id} reset by DialogueManager.")
            return True
        return False

    def close_session(self, session_id: str) -> Optional[dict]:
        """
        Close a session and return its export data.

        Args:
            session_id: Session to close

        Returns:
            Exported session dict or None if not found
        """
        if session_id in self._sessions:
            session = self._sessions.pop(session_id)
            export = session.export()
            logger.info(f"Session {session_id} closed and exported.")
            return export
        return None

    def get_active_session_count(self) -> int:
        """Return the number of currently active sessions."""
        return len(self._sessions)

    def get_all_session_ids(self) -> List[str]:
        """Return all active session IDs."""
        return list(self._sessions.keys())

    def _get_session(self, session_id: str) -> ConversationSession:
        """Retrieve a session by ID, auto-creating if missing."""
        if session_id not in self._sessions:
            logger.warning(f"Session {session_id} not found. Auto-creating new session.")
            new_id = self.start_session()
            return self._sessions[new_id]
        return self._sessions[session_id]


# Global singleton instance
dialogue_manager = DialogueManager()
