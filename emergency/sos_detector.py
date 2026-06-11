"""
SignBridge AI — Layer 12: SOS Detector
Monitors sign token sequences for emergency trigger patterns.
Operates in real-time on each frame's gesture output.
Provides confidence-scored emergency event classification.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from config.logger import setup_logger

logger = setup_logger("emergency.sos_detector")

# Emergency severity levels
LEVEL_CRITICAL = "CRITICAL"  # Immediate life threat
LEVEL_URGENT = "URGENT"  # Urgent medical/safety need
LEVEL_ALERT = "ALERT"  # Potential emergency


# Token patterns mapped to severity
CRITICAL_PATTERNS = [
    {"HEART", "ATTACK"},
    {"CHEST", "PAIN"},
    {"NOT", "BREATHE"},
    {"CANNOT", "BREATHE"},
    {"CAN'T", "BREATHE"},
    {"UNCONSCIOUS"},
    {"SEIZURE"},
    {"DYING"},
    {"SOS"},
]

URGENT_PATTERNS = [
    {"EMERGENCY"},
    {"AMBULANCE"},
    {"BLEEDING"},
    {"FIRE"},
    {"DANGER"},
    {"TRAPPED"},
    {"CALL", "POLICE"},
    {"CALL", "DOCTOR"},
    {"HEART"},
    {"FALLING"},
]

ALERT_PATTERNS = [
    {"HELP"},
    {"PAIN"},
    {"HURT"},
    {"LOST"},
    {"ALARM"},
]


@dataclass
class SOSEvent:
    """Represents a detected emergency event."""

    severity: str
    triggered_tokens: list[str]
    matching_pattern: list[str]
    confidence: float
    timestamp: datetime
    message: str


class SOSDetector:
    """
    Real-time emergency sign sequence detector.
    Analyzes each gesture output from Layer 4 for emergency patterns.
    Uses pattern matching with window accumulation for robust detection.
    """

    def __init__(self, window_size: int = 5, min_confidence: float = 0.6):
        self._window_size = window_size
        self._min_confidence = min_confidence
        self._token_window: list[str] = []
        self._last_event: SOSEvent | None = None
        self._total_sos_events = 0
        logger.info(
            f"SOSDetector initialized (window={window_size}, threshold={min_confidence})"
        )

    def update(self, new_tokens: list[str]) -> SOSEvent | None:
        """
        Update the detector with new tokens from the current gesture frame.
        Maintains a rolling window and checks for emergency patterns.

        Args:
            new_tokens: New recognized tokens from Layer 4

        Returns:
            SOSEvent if an emergency is detected, None otherwise
        """
        # Add to rolling window
        self._token_window.extend([t.upper() for t in new_tokens])
        if len(self._token_window) > self._window_size * 3:
            self._token_window = self._token_window[-(self._window_size * 3) :]

        window_set = set(self._token_window)

        # Check CRITICAL patterns (highest priority)
        for pattern in CRITICAL_PATTERNS:
            if pattern.issubset(window_set) or (
                len(pattern) == 1 and pattern.issubset(window_set)
            ):
                return self._create_event(
                    LEVEL_CRITICAL, list(window_set & pattern), list(pattern), 0.98
                )

        # Check URGENT patterns
        for pattern in URGENT_PATTERNS:
            if pattern.issubset(window_set):
                return self._create_event(
                    LEVEL_URGENT, list(window_set & pattern), list(pattern), 0.88
                )

        # Check ALERT patterns
        for pattern in ALERT_PATTERNS:
            if pattern.issubset(window_set):
                return self._create_event(
                    LEVEL_ALERT, list(window_set & pattern), list(pattern), 0.75
                )

        return None

    def check_tokens(self, tokens: list[str]) -> SOSEvent | None:
        """
        One-shot check of a token list without updating the window.
        Use this for single frame checks without accumulation.

        Args:
            tokens: Token list to check

        Returns:
            SOSEvent if emergency detected, None otherwise
        """
        token_set = {t.upper() for t in tokens}

        for pattern in CRITICAL_PATTERNS:
            if pattern.issubset(token_set):
                return self._create_event(
                    LEVEL_CRITICAL, list(token_set & pattern), list(pattern), 0.98
                )

        for pattern in URGENT_PATTERNS:
            if pattern.issubset(token_set):
                return self._create_event(
                    LEVEL_URGENT, list(token_set & pattern), list(pattern), 0.88
                )

        for pattern in ALERT_PATTERNS:
            if token_set & pattern:
                return self._create_event(
                    LEVEL_ALERT, list(token_set & pattern), list(pattern), 0.75
                )

        return None

    def _create_event(
        self, severity: str, triggered: list[str], pattern: list[str], confidence: float
    ) -> SOSEvent:
        """Create and record an SOSEvent."""
        messages = {
            LEVEL_CRITICAL: "🚨 CRITICAL EMERGENCY DETECTED — Immediate action required!",
            LEVEL_URGENT: "🆘 URGENT: Emergency situation detected — Act now.",
            LEVEL_ALERT: "⚠️ ALERT: Possible emergency signs detected.",
        }
        event = SOSEvent(
            severity=severity,
            triggered_tokens=triggered,
            matching_pattern=pattern,
            confidence=confidence,
            timestamp=datetime.now(UTC),
            message=messages.get(severity, "Emergency detected."),
        )
        self._last_event = event
        self._total_sos_events += 1
        logger.warning(
            f"SOS Event [{severity}]: tokens={triggered}, pattern={pattern}, conf={confidence}"
        )
        return event

    def get_last_event(self) -> SOSEvent | None:
        """Return the most recently detected SOS event."""
        return self._last_event

    def get_event_count(self) -> int:
        """Return total number of SOS events detected in this session."""
        return self._total_sos_events

    def reset_window(self) -> None:
        """Clear the token accumulation window."""
        self._token_window.clear()
        logger.info("SOS window reset.")

    def reset_session(self) -> None:
        """Full reset: clear window, last event, and event count."""
        self._token_window.clear()
        self._last_event = None
        self._total_sos_events = 0
        logger.info("SOSDetector session reset.")


sos_detector = SOSDetector()
