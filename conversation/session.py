"""
SignBridge AI — Layer 7: Conversation Session
Manages a complete conversation session combining message threading,
context tracking, and emotion monitoring.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict

from conversation.message_thread import MessageThread
from conversation.emotion_tone import emotion_detector
from conversation.schemas import (
    Message, MessageRole, EmotionTone, DialogueTurn, SessionSummary
)
from config.logger import setup_logger

logger = setup_logger("conversation.session")


class ConversationSession:
    """
    A complete sign language conversation session.

    Combines:
    - MessageThread: stores all messages
    - EmotionToneDetector: classifies each turn
    - Context: rolling window of recent translations for grammar engine
    - Statistics: turn count, emotion history, language usage
    """

    def __init__(self, language: str = "English"):
        self.session_id = str(uuid.uuid4())
        self.language = language
        self.started_at = datetime.now(timezone.utc)
        self._thread = MessageThread(session_id=self.session_id, language=language)
        self._turns: List[DialogueTurn] = []
        self._emotion_history: List[EmotionTone] = []
        self._languages_used: set = {language}
        self._turn_index = 0
        logger.info(f"ConversationSession started: {self.session_id} ({language})")

    def process_signer_input(
        self,
        signs: List[str],
        translated_text: str,
        language: str = "English",
        confidence: float = 1.0,
    ) -> DialogueTurn:
        """
        Process a complete signer input turn: detect emotion, add to thread,
        generate response suggestion, and record the turn.

        Args:
            signs: Recognized sign tokens
            translated_text: Layer 5 translated text
            language: Target language
            confidence: Translation confidence

        Returns:
            DialogueTurn with all derived metadata
        """
        self._languages_used.add(language)

        # Detect emotion
        emotion = emotion_detector.detect(signs, translated_text)
        self._emotion_history.append(emotion)

        # Get response suggestion
        suggestion = emotion_detector.get_response_suggestion(emotion)

        # Add to message thread
        self._thread.add_signer_message(
            signs=signs,
            text=translated_text,
            language=language,
            confidence=confidence,
            emotion=emotion,
        )

        # Build dialogue turn record
        turn = DialogueTurn(
            turn_index=self._turn_index,
            input_signs=signs,
            english_intermediate=translated_text,
            final_text=translated_text,
            language=language,
            emotion=emotion,
            confidence=confidence,
            response_suggestion=suggestion,
            timestamp=datetime.now(timezone.utc),
        )
        self._turns.append(turn)
        self._turn_index += 1

        logger.info(
            f"Signer turn {self._turn_index}: emotion={emotion.value}, "
            f"confidence={confidence:.2f}, text='{translated_text[:60]}'"
        )
        return turn

    def add_listener_reply(self, text: str, language: str = "English") -> Message:
        """
        Record a message from the hearing participant.

        Args:
            text: Typed text from the listener
            language: Language of the message

        Returns:
            Created Message
        """
        self._languages_used.add(language)
        return self._thread.add_listener_message(text=text, language=language)

    def get_all_messages(self) -> List[Message]:
        """Return all messages in chronological order."""
        return self._thread.get_all_messages()

    def get_recent_context(self, n: int = 5) -> List[str]:
        """
        Return the last N signer translation strings for context injection.

        Args:
            n: Number of recent turns to retrieve

        Returns:
            List of translation strings
        """
        signer_messages = self._thread.get_signer_messages()
        return [m.text for m in signer_messages[-n:]]

    def get_summary(self) -> SessionSummary:
        """
        Build a session summary for display or logging.

        Returns:
            SessionSummary with aggregated statistics
        """
        now = datetime.now(timezone.utc)
        elapsed = (now - self.started_at).total_seconds()

        # Dominant emotion: most frequent non-neutral
        emotion_counts: Dict[EmotionTone, int] = {}
        for e in self._emotion_history:
            emotion_counts[e] = emotion_counts.get(e, 0) + 1

        dominant = EmotionTone.NEUTRAL
        if emotion_counts:
            dominant = max(emotion_counts, key=lambda k: emotion_counts[k])

        return SessionSummary(
            session_id=self.session_id,
            total_turns=len(self._turns),
            total_messages=self._thread.get_message_count(),
            languages_used=list(self._languages_used),
            duration_seconds=round(elapsed, 1),
            dominant_emotion=dominant,
            started_at=self.started_at,
            last_activity=self._turns[-1].timestamp if self._turns else None,
            sign_tokens_processed=self._thread.get_signer_sign_count(),
        )

    def export(self) -> dict:
        """Export the full session as a JSON-serializable dict."""
        summary = self.get_summary()
        return {
            **self._thread.to_export_dict(),
            "summary": {
                "total_turns": summary.total_turns,
                "dominant_emotion": summary.dominant_emotion.value,
                "languages_used": summary.languages_used,
                "duration_seconds": summary.duration_seconds,
                "sign_tokens_processed": summary.sign_tokens_processed,
            }
        }

    def reset(self) -> None:
        """Clear all messages and turns but keep session active."""
        self._thread.clear()
        self._turns.clear()
        self._emotion_history.clear()
        self._turn_index = 0
        logger.info(f"Session {self.session_id} reset.")
