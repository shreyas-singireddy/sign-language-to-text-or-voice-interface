"""
SignBridge AI — Layer 9: Metrics Collector
Captures per-session analytics metrics in real-time:
  - Translation events (gestures, confidence, language, timestamp)
  - Speech synthesis events
  - Session duration and activity
  - Gesture frequency tracking
  - Emotion tone distribution

Stores all metrics in-memory with optional export to MongoDB.
"""

import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from config.logger import setup_logger

logger = setup_logger("analytics.metrics_collector")


class TranslationEvent:
    """Immutable record of a single translation event."""

    def __init__(
        self,
        signs: list[str],
        translated_text: str,
        language: str,
        confidence: float,
        provider: str,
        emotion: str,
        elapsed_ms: float,
    ):
        self.signs = list(signs)
        self.translated_text = translated_text
        self.language = language
        self.confidence = confidence
        self.provider = provider
        self.emotion = emotion
        self.elapsed_ms = elapsed_ms
        self.timestamp = datetime.now(UTC)


class MetricsCollector:
    """
    Real-time metrics collector for SignBridge AI analytics platform.
    Tracks all translation events, session activity, and system performance.
    """

    def __init__(self):
        self._translation_events: list[TranslationEvent] = []
        self._speech_events: list[dict[str, Any]] = []
        self._session_start: float = time.time()
        self._gesture_frequency: dict[str, int] = defaultdict(int)
        self._language_counts: dict[str, int] = defaultdict(int)
        self._emotion_counts: dict[str, int] = defaultdict(int)
        self._confidence_samples: list[float] = []
        self._latency_samples: list[float] = []
        logger.info("MetricsCollector initialized.")

    def record_translation(
        self,
        signs: list[str],
        translated_text: str,
        language: str,
        confidence: float,
        provider: str = "rule_based",
        emotion: str = "neutral",
        elapsed_ms: float = 0.0,
    ) -> None:
        """
        Record a completed translation event.

        Args:
            signs: Sign tokens processed
            translated_text: Final translated text
            language: Target language
            confidence: Translation confidence
            provider: Provider used
            emotion: Detected emotion
            elapsed_ms: Processing latency in milliseconds
        """
        event = TranslationEvent(
            signs=signs,
            translated_text=translated_text,
            language=language,
            confidence=confidence,
            provider=provider,
            emotion=emotion,
            elapsed_ms=elapsed_ms,
        )
        self._translation_events.append(event)

        # Update frequency maps
        for sign in signs:
            self._gesture_frequency[sign.upper()] += 1

        self._language_counts[language] += 1
        self._emotion_counts[emotion] += 1
        self._confidence_samples.append(confidence)
        if elapsed_ms > 0:
            self._latency_samples.append(elapsed_ms)

        logger.debug(
            f"Translation event recorded: {signs} → '{translated_text[:40]}' "
            f"({language}, conf={confidence:.2f})"
        )

    def record_speech_synthesis(
        self, text: str, language: str, provider: str, success: bool
    ) -> None:
        """
        Record a TTS synthesis event.

        Args:
            text: Text that was synthesized
            language: Language of synthesis
            provider: TTS provider used
            success: Whether synthesis succeeded
        """
        self._speech_events.append(
            {
                "text": text[:100],
                "language": language,
                "provider": provider,
                "success": success,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def get_total_translations(self) -> int:
        """Return total number of translation events."""
        return len(self._translation_events)

    def get_average_confidence(self) -> float:
        """Return average confidence across all translation events."""
        if not self._confidence_samples:
            return 0.0
        return round(sum(self._confidence_samples) / len(self._confidence_samples), 3)

    def get_average_latency_ms(self) -> float:
        """Return average translation latency in milliseconds."""
        if not self._latency_samples:
            return 0.0
        return round(sum(self._latency_samples) / len(self._latency_samples), 1)

    def get_gesture_frequency(self) -> dict[str, int]:
        """Return gesture token frequency map (descending order)."""
        return dict(
            sorted(self._gesture_frequency.items(), key=lambda x: x[1], reverse=True)
        )

    def get_language_distribution(self) -> dict[str, int]:
        """Return language usage counts."""
        return dict(self._language_counts)

    def get_emotion_distribution(self) -> dict[str, int]:
        """Return emotion tone distribution."""
        return dict(self._emotion_counts)

    def get_top_gestures(self, n: int = 10) -> list[dict[str, Any]]:
        """
        Return top N most frequent gestures.

        Args:
            n: Number of top gestures to return

        Returns:
            List of dicts with 'gesture' and 'count' keys
        """
        freq = self.get_gesture_frequency()
        top = list(freq.items())[:n]
        return [{"gesture": g, "count": c} for g, c in top]

    def get_daily_activity(self) -> dict[str, int]:
        """
        Return translation counts grouped by date string.

        Returns:
            Dict of date_string → count
        """
        daily: dict[str, int] = defaultdict(int)
        for event in self._translation_events:
            date_str = event.timestamp.strftime("%Y-%m-%d")
            daily[date_str] += 1
        return dict(sorted(daily.items()))

    def get_hourly_activity(self) -> dict[str, int]:
        """
        Return translation counts grouped by hour of day.

        Returns:
            Dict of 'HH:00' → count
        """
        hourly: dict[str, int] = defaultdict(int)
        for event in self._translation_events:
            hour_str = event.timestamp.strftime("%H:00")
            hourly[hour_str] += 1
        return dict(sorted(hourly.items()))

    def get_confidence_histogram(self, bins: int = 10) -> dict[str, int]:
        """
        Return confidence scores bucketed into histogram bins.

        Args:
            bins: Number of histogram buckets

        Returns:
            Dict of 'X%-Y%' bucket labels → count
        """
        if not self._confidence_samples:
            return {}

        bucket_size = 1.0 / bins
        histogram: dict[str, int] = defaultdict(int)
        for score in self._confidence_samples:
            bucket_index = min(int(score / bucket_size), bins - 1)
            low = int(bucket_index * bucket_size * 100)
            high = int((bucket_index + 1) * bucket_size * 100)
            label = f"{low}%–{high}%"
            histogram[label] += 1
        return dict(histogram)

    def get_session_duration_seconds(self) -> float:
        """Return total session duration in seconds since collector was initialized."""
        return round(time.time() - self._session_start, 1)

    def get_full_metrics_snapshot(self) -> dict[str, Any]:
        """
        Return a complete snapshot of all collected metrics.
        Ideal for database storage or dashboard rendering.
        """
        return {
            "total_translations": self.get_total_translations(),
            "average_confidence": self.get_average_confidence(),
            "average_latency_ms": self.get_average_latency_ms(),
            "gesture_frequency": self.get_gesture_frequency(),
            "language_distribution": self.get_language_distribution(),
            "emotion_distribution": self.get_emotion_distribution(),
            "daily_activity": self.get_daily_activity(),
            "hourly_activity": self.get_hourly_activity(),
            "top_gestures": self.get_top_gestures(10),
            "session_duration_seconds": self.get_session_duration_seconds(),
            "total_speech_events": len(self._speech_events),
            "confidence_histogram": self.get_confidence_histogram(),
        }

    def reset(self) -> None:
        """Clear all collected metrics."""
        self._translation_events.clear()
        self._speech_events.clear()
        self._gesture_frequency.clear()
        self._language_counts.clear()
        self._emotion_counts.clear()
        self._confidence_samples.clear()
        self._latency_samples.clear()
        self._session_start = time.time()
        logger.info("MetricsCollector reset.")


# Global singleton instance
metrics_collector = MetricsCollector()
