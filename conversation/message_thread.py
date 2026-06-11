"""
SignBridge AI — Layer 7: Message Thread
Manages the ordered sequence of messages in a conversation session.
Provides insertion, retrieval, search, and export functionality.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from conversation.schemas import Message, MessageRole, EmotionTone, ConversationThread
from config.logger import setup_logger

logger = setup_logger("conversation.message_thread")


class MessageThread:
    """
    Ordered conversation message thread for a single session.
    Acts as the persistent in-memory store for all messages
    exchanged during a conversation session.
    """

    def __init__(self, session_id: str, language: str = "English"):
        self._thread = ConversationThread(
            session_id=session_id,
            messages=[],
            started_at=datetime.now(timezone.utc),
            language=language,
            participant_count=2,
            is_active=True,
        )
        logger.info(f"MessageThread created for session {session_id}")

    def add_signer_message(
        self,
        signs: List[str],
        text: str,
        language: str = "English",
        confidence: float = 1.0,
        emotion: EmotionTone = EmotionTone.NEUTRAL,
    ) -> Message:
        """
        Add a message from the sign language user (signer).

        Args:
            signs: Original sign tokens
            text: Translated text
            language: Language of the translation
            confidence: Translation confidence score
            emotion: Detected emotion tone

        Returns:
            Created Message object
        """
        message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.SIGNER,
            original_signs=signs,
            text=text,
            language=language,
            emotion=emotion,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc),
        )
        self._thread.messages.append(message)
        logger.debug(f"Signer message added: '{text[:60]}'")
        return message

    def add_listener_message(
        self,
        text: str,
        language: str = "English",
    ) -> Message:
        """
        Add a message from the hearing participant (listener).

        Args:
            text: Typed or spoken text from the listener
            language: Language of the message

        Returns:
            Created Message object
        """
        message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.LISTENER,
            original_signs=[],
            text=text,
            language=language,
            emotion=EmotionTone.NEUTRAL,
            confidence=1.0,
            timestamp=datetime.now(timezone.utc),
        )
        self._thread.messages.append(message)
        logger.debug(f"Listener message added: '{text[:60]}'")
        return message

    def add_system_message(self, text: str) -> Message:
        """
        Add a system notification message to the thread.

        Args:
            text: System message content

        Returns:
            Created Message object
        """
        message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.SYSTEM,
            original_signs=[],
            text=text,
            language="English",
            emotion=EmotionTone.NEUTRAL,
            confidence=1.0,
            timestamp=datetime.now(timezone.utc),
        )
        self._thread.messages.append(message)
        return message

    def get_all_messages(self) -> List[Message]:
        """Return all messages in chronological order."""
        return list(self._thread.messages)

    def get_last_n_messages(self, n: int) -> List[Message]:
        """Return the last N messages."""
        return self._thread.messages[-n:] if n > 0 else []

    def get_signer_messages(self) -> List[Message]:
        """Return only messages from the signer."""
        return [m for m in self._thread.messages if m.role == MessageRole.SIGNER]

    def get_message_count(self) -> int:
        """Return total message count."""
        return len(self._thread.messages)

    def get_signer_sign_count(self) -> int:
        """Return total number of sign tokens processed across all signer messages."""
        return sum(len(m.original_signs) for m in self._thread.messages if m.role == MessageRole.SIGNER)

    def get_full_thread(self) -> ConversationThread:
        """Return the full ConversationThread model."""
        return self._thread

    def to_export_dict(self) -> dict:
        """
        Export the full thread as a serializable dictionary for logging or storage.
        """
        return {
            "session_id": self._thread.session_id,
            "started_at": self._thread.started_at.isoformat(),
            "language": self._thread.language,
            "message_count": len(self._thread.messages),
            "messages": [
                {
                    "id": m.id,
                    "role": m.role.value,
                    "signs": m.original_signs,
                    "text": m.text,
                    "language": m.language,
                    "emotion": m.emotion.value,
                    "confidence": m.confidence,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in self._thread.messages
            ]
        }

    def clear(self) -> None:
        """Clear all messages from the thread."""
        self._thread.messages = []
        logger.info(f"Thread cleared for session {self._thread.session_id}")

    def close(self) -> None:
        """Mark the thread as inactive (session ended)."""
        self._thread.is_active = False
        logger.info(f"Thread closed for session {self._thread.session_id}")
