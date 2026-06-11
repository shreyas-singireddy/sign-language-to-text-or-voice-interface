"""
SignBridge AI — Layer 12: Alert Dispatcher
Multi-channel emergency alert dispatcher.
On emergency detection, dispatches alerts to:
  1. UI (Streamlit visual alert)
  2. Log (structured emergency log)
  3. Webhook (optional external endpoint via httpx)
  4. Database (MongoDB alert record)
"""

import json
from datetime import UTC, datetime
from typing import Any

from config.logger import setup_logger
from emergency.sos_detector import SOSEvent

logger = setup_logger("emergency.alert_dispatcher")


class AlertRecord:
    """Immutable record of a dispatched alert."""

    def __init__(self, event: SOSEvent, channels_notified: list[str]):
        self.event = event
        self.channels_notified = channels_notified
        self.dispatched_at = datetime.now(UTC)
        self.alert_id = f"ALT_{int(self.dispatched_at.timestamp())}"

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "severity": self.event.severity,
            "triggered_tokens": self.event.triggered_tokens,
            "matching_pattern": self.event.matching_pattern,
            "confidence": self.event.confidence,
            "message": self.event.message,
            "channels": self.channels_notified,
            "dispatched_at": self.dispatched_at.isoformat(),
            "event_timestamp": self.event.timestamp.isoformat(),
        }


class AlertDispatcher:
    """
    Multi-channel emergency alert dispatcher.
    Logs, records, and optionally webhooks emergency events.
    """

    def __init__(self, webhook_url: str | None = None):
        self._webhook_url = webhook_url
        self._alert_log: list[AlertRecord] = []
        logger.info(
            f"AlertDispatcher initialized (webhook={'enabled' if webhook_url else 'disabled'})"
        )

    def dispatch(self, event: SOSEvent, user_name: str = "Unknown User") -> AlertRecord:
        """
        Dispatch an emergency alert through all configured channels.

        Args:
            event: SOS event to dispatch
            user_name: Name of the user in emergency

        Returns:
            AlertRecord with dispatch details
        """
        channels_notified = []

        # Channel 1: Structured emergency log
        self._log_alert(event, user_name)
        channels_notified.append("log")

        # Channel 2: Webhook (if configured)
        if self._webhook_url:
            webhook_success = self._send_webhook(event, user_name)
            if webhook_success:
                channels_notified.append("webhook")

        # Channel 3: In-memory record
        record = AlertRecord(event=event, channels_notified=channels_notified)
        self._alert_log.append(record)
        channels_notified.append("in_memory")

        logger.warning(
            f"EMERGENCY DISPATCHED [{event.severity}]: {event.message} "
            f"| Channels: {channels_notified}"
        )
        return record

    def _log_alert(self, event: SOSEvent, user_name: str) -> None:
        """Write structured emergency log entry."""
        log_entry = {
            "EMERGENCY_ALERT": True,
            "severity": event.severity,
            "user": user_name,
            "tokens": event.triggered_tokens,
            "pattern": event.matching_pattern,
            "confidence": event.confidence,
            "message": event.message,
            "timestamp": event.timestamp.isoformat(),
        }
        logger.critical(f"EMERGENCY_LOG: {json.dumps(log_entry)}")

    def _send_webhook(self, event: SOSEvent, user_name: str) -> bool:
        """Send emergency data to a webhook endpoint."""
        try:
            import httpx

            payload = {
                "type": "signbridge_emergency",
                "severity": event.severity,
                "user": user_name,
                "message": event.message,
                "triggered_tokens": event.triggered_tokens,
                "confidence": event.confidence,
                "timestamp": event.timestamp.isoformat(),
            }
            response = httpx.post(
                self._webhook_url,
                json=payload,
                timeout=3.0,
                headers={
                    "Content-Type": "application/json",
                    "X-SignBridge-Alert": event.severity,
                },
            )
            logger.info(f"Webhook dispatched: {response.status_code}")
            return response.status_code < 400
        except Exception as exc:
            logger.error(f"Webhook dispatch failed: {exc}")
            return False

    def get_alert_history(self) -> list[dict[str, Any]]:
        """Return all dispatched alerts as serializable dicts."""
        return [record.to_dict() for record in self._alert_log]

    def get_alert_count(self) -> int:
        """Return total number of dispatched alerts."""
        return len(self._alert_log)

    def get_recent_alerts(self, n: int = 5) -> list[dict[str, Any]]:
        """Return the N most recent alert records."""
        return [r.to_dict() for r in self._alert_log[-n:]]

    def clear_history(self) -> None:
        """Clear the in-memory alert log."""
        self._alert_log.clear()
        logger.info("Alert history cleared.")

    def configure_webhook(self, url: str) -> None:
        """Update the webhook URL at runtime."""
        self._webhook_url = url
        logger.info(f"Webhook configured: {url}")


alert_dispatcher = AlertDispatcher()
