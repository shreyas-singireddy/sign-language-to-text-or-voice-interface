"""
SignBridge AI — Layer 12: Panic Protocol
Activates the full emergency protocol when a critical SOS event is detected.
Coordinates: dispatcher alert + TTS emergency audio + UI lockdown CSS.
"""

from config.logger import setup_logger
from emergency.alert_dispatcher import AlertDispatcher, AlertRecord
from emergency.sos_detector import LEVEL_CRITICAL, LEVEL_URGENT, SOSEvent

logger = setup_logger("emergency.panic_protocol")

# UI alert HTML for different severity levels
ALERT_HTML = {
    LEVEL_CRITICAL: """
    <div style="
        background: #D02020;
        border: 5px solid #FFFFFF;
        color: #FFFFFF;
        font-family: 'Space Grotesk', 'Outfit', monospace;
        font-weight: 900;
        font-size: 1.4rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 24px 30px;
        margin-bottom: 20px;
        box-shadow: 10px 10px 0px #000000;
        animation: pulse-alert 1s infinite;
    ">
        🚨 CRITICAL EMERGENCY 🚨<br/>
        <span style="font-size: 1rem; font-weight: 700;">{message}</span>
    </div>
    <style>
    @keyframes pulse-alert {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    </style>
    """,
    LEVEL_URGENT: """
    <div style="
        background: #E06010;
        border: 4px solid #121212;
        color: #FFFFFF;
        font-family: 'Space Grotesk', 'Outfit', monospace;
        font-weight: 900;
        font-size: 1.25rem;
        text-transform: uppercase;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 8px 8px 0px #121212;
    ">
        🆘 URGENT EMERGENCY<br/>
        <span style="font-size: 0.95rem; font-weight: 700;">{message}</span>
    </div>
    """,
    "ALERT": """
    <div style="
        background: #F0C020;
        border: 3px solid #121212;
        color: #121212;
        font-family: 'Space Grotesk', 'Outfit', monospace;
        font-weight: 900;
        font-size: 1.1rem;
        text-transform: uppercase;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 6px 6px 0px #121212;
    ">
        ⚠️ EMERGENCY ALERT<br/>
        <span style="font-size: 0.85rem; font-weight: 700;">{message}</span>
    </div>
    """,
}


class PanicProtocol:
    """
    Layer 12 Panic Protocol Coordinator.
    Activates when SOSDetector fires a CRITICAL or URGENT event.

    Actions on activation:
    1. Dispatch alert via AlertDispatcher (log + webhook)
    2. Prepare emergency TTS text for audio playback
    3. Return UI alert HTML for Streamlit injection
    4. Record activation in session log
    """

    def __init__(self, dispatcher: AlertDispatcher):
        self._dispatcher = dispatcher
        self._activations: list[dict] = []
        self._is_active = False
        logger.info("PanicProtocol initialized.")

    def activate(self, event: SOSEvent, user_name: str = "Unknown User") -> dict:
        """
        Activate the panic protocol for a detected SOS event.

        Args:
            event: SOSEvent from SOSDetector
            user_name: Name of the user in emergency

        Returns:
            Dict with:
            - alert_record: AlertRecord from dispatcher
            - ui_html: Streamlit-injectable HTML
            - tts_text: Text to synthesize via TTS engine
            - severity: Severity level string
            - is_critical: Boolean for critical vs. urgent
        """
        self._is_active = True

        # Dispatch to all channels
        alert_record: AlertRecord = self._dispatcher.dispatch(event, user_name)

        # Generate UI HTML
        ui_html = self._generate_ui_html(event)

        # Generate TTS text
        tts_text = self._generate_tts_text(event, user_name)

        # Record activation
        activation = {
            "alert_id": alert_record.alert_id,
            "severity": event.severity,
            "tts_text": tts_text,
            "user_name": user_name,
            "timestamp": event.timestamp.isoformat(),
        }
        self._activations.append(activation)

        logger.critical(f"PanicProtocol ACTIVATED [{event.severity}] for user '{user_name}': {event.message}")

        return {
            "alert_record": alert_record,
            "ui_html": ui_html,
            "tts_text": tts_text,
            "severity": event.severity,
            "is_critical": event.severity == LEVEL_CRITICAL,
        }

    def deactivate(self) -> None:
        """Deactivate the panic state (after situation resolved)."""
        self._is_active = False
        logger.info("PanicProtocol deactivated.")

    def is_active(self) -> bool:
        """Check if panic protocol is currently active."""
        return self._is_active

    def get_activation_count(self) -> int:
        """Return number of times protocol has been activated."""
        return len(self._activations)

    def get_activation_history(self) -> list[dict]:
        """Return full activation history."""
        return list(self._activations)

    def _generate_ui_html(self, event: SOSEvent) -> str:
        """Generate the Streamlit-injectable alert HTML for this event."""
        template = ALERT_HTML.get(event.severity, ALERT_HTML["ALERT"])
        return template.format(message=event.message)

    def _generate_tts_text(self, event: SOSEvent, user_name: str) -> str:
        """
        Generate the TTS emergency speech text.
        Formatted for maximum clarity in a real emergency.
        """
        if event.severity == LEVEL_CRITICAL:
            return (
                f"CRITICAL EMERGENCY. {user_name} needs immediate help. "
                f"{event.message} Please call emergency services immediately."
            )
        elif event.severity == LEVEL_URGENT:
            return f"Emergency alert. {user_name} needs urgent assistance. " f"{event.message}"
        else:
            return f"Alert. {user_name} may need help. {event.message}"

    def generate_quick_sos_html(self, phrases: list[str]) -> str:
        """
        Generate a quick-access SOS phrase panel HTML for the Emergency page.

        Args:
            phrases: List of emergency phrases to display as buttons

        Returns:
            HTML string with phrase buttons
        """
        buttons_html = ""
        for phrase in phrases:
            buttons_html += f"""
            <div style="
                background: #D02020;
                color: #FFFFFF;
                border: 3px solid #121212;
                box-shadow: 5px 5px 0px #121212;
                padding: 14px 20px;
                margin-bottom: 12px;
                font-family: 'Outfit', sans-serif;
                font-weight: 800;
                font-size: 1rem;
                text-transform: uppercase;
                cursor: pointer;
                letter-spacing: 0.05em;
                transition: transform 0.1s;
            ">
                🆘 {phrase}
            </div>
            """

        return f"""
        <div style="padding: 10px 0;">
            <div style="
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 900;
                font-size: 1.2rem;
                text-transform: uppercase;
                margin-bottom: 16px;
                border-bottom: 4px solid #D02020;
                padding-bottom: 8px;
            ">🚨 Quick SOS Phrases</div>
            {buttons_html}
        </div>
        """


from emergency.alert_dispatcher import alert_dispatcher as _alert_dispatcher_singleton

panic_protocol = PanicProtocol(dispatcher=_alert_dispatcher_singleton)
