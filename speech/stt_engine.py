"""
SignBridge AI — Layer 6: STT Engine
Speech-to-Text engine that bridges the browser's Web Speech API
to the Streamlit backend. Since Python cannot directly access the microphone
in a browser context, STT is implemented as:
  1. Browser-side: JavaScript Web Speech API captures voice and sends transcript
  2. Python-side: STTEngine exposes generate_input_html() for st.components injection
     and processes returned transcripts.

The engine also provides a text-input fallback for environments without mic access.
"""

from config.logger import setup_logger
from speech.providers.browser_provider import BROWSER_LANG_MAP
from speech.schemas import STTProvider, STTResult

logger = setup_logger("speech.stt_engine")


class STTEngine:
    """
    Layer 6 Speech-to-Text Engine.
    Provides browser-native STT via injected Web Speech API JavaScript.

    Architecture:
        STTEngine.get_stt_html(lang_code) → HTML with <script>
        → st.components.v1.html(html, height=0)
        → Browser captures speech
        → Transcript is captured via Streamlit query_params or session state

    Note: Full bidirectional browser→Python communication in Streamlit requires
    a custom component. This engine provides the JS scaffolding and a text
    input fallback that always works.
    """

    def __init__(self):
        self._default_lang = "en-US"
        logger.info("STTEngine initialized (browser Web Speech API + text input fallback)")

    def get_stt_html(self, lang_code: str = "en-US", button_label: str = "🎤 Start Listening") -> str:
        """
        Generate HTML + JavaScript for browser-side speech recognition.
        The transcript is displayed in the page and can be copied.

        Args:
            lang_code: BCP-47 language code for recognition
            button_label: Label for the microphone activation button

        Returns:
            Complete HTML string for injection via st.components.v1.html()
        """
        lang = BROWSER_LANG_MAP.get(lang_code, "en-US")
        return f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: transparent; padding: 0; margin: 0; }}
            #stt-container {{
                border: 2.5px solid #121212;
                padding: 12px 16px;
                background: #FFFFFF;
                box-shadow: 4px 4px 0 #121212;
            }}
            #stt-status {{ font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #555; margin-bottom: 8px; }}
            #stt-transcript {{
                font-size: 1.1rem;
                font-weight: 800;
                min-height: 40px;
                color: #121212;
                border-top: 2px solid #E0E0E0;
                padding-top: 8px;
                margin-top: 6px;
                word-break: break-word;
            }}
            button {{
                font-family: 'Segoe UI', sans-serif;
                font-weight: 800;
                font-size: 0.95rem;
                text-transform: uppercase;
                border: 2.5px solid #121212;
                box-shadow: 3px 3px 0 #121212;
                background: #F0C020;
                color: #121212;
                padding: 8px 16px;
                cursor: pointer;
                transition: all 0.1s ease;
            }}
            button:hover {{ background: #D02020; color: #FFF; }}
            button.listening {{ background: #D02020; color: #FFF; animation: pulse 1s infinite; }}
            @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.6}} }}
        </style>
        </head>
        <body>
        <div id="stt-container">
            <div id="stt-status">Web Speech API — Ready</div>
            <button id="stt-btn" onclick="toggleListening()">{button_label}</button>
            <div id="stt-transcript">Transcript will appear here...</div>
        </div>
        <script>
        var recognition = null;
        var isListening = false;

        function toggleListening() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                document.getElementById('stt-status').innerText = 'Speech API not supported in this browser.';
                return;
            }}
            if (isListening) {{
                recognition.stop();
                return;
            }}
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = '{lang}';
            recognition.interimResults = true;
            recognition.continuous = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {{
                isListening = true;
                document.getElementById('stt-status').innerText = '🔴 Listening...';
                document.getElementById('stt-btn').classList.add('listening');
                document.getElementById('stt-btn').innerText = '⏹ Stop Listening';
            }};

            recognition.onresult = function(event) {{
                var transcript = '';
                for (var i = event.resultIndex; i < event.results.length; i++) {{
                    transcript += event.results[i][0].transcript;
                }}
                document.getElementById('stt-transcript').innerText = transcript;
            }};

            recognition.onerror = function(event) {{
                document.getElementById('stt-status').innerText = 'Error: ' + event.error;
                isListening = false;
                document.getElementById('stt-btn').classList.remove('listening');
                document.getElementById('stt-btn').innerText = '{button_label}';
            }};

            recognition.onend = function() {{
                isListening = false;
                document.getElementById('stt-status').innerText = '✅ Recognition Complete';
                document.getElementById('stt-btn').classList.remove('listening');
                document.getElementById('stt-btn').innerText = '{button_label}';
            }};

            recognition.start();
        }}
        </script>
        </body>
        </html>
        """

    def process_transcript(self, transcript: str, lang_code: str = "en-US") -> STTResult:
        """
        Process a transcript string received from the browser or text input.

        Args:
            transcript: Raw speech transcript text
            lang_code: Language of the transcript

        Returns:
            STTResult with processed transcript and metadata
        """
        cleaned = transcript.strip()
        if not cleaned:
            return STTResult(
                transcript="",
                confidence=0.0,
                provider_used=STTProvider.BROWSER,
                language=lang_code,
                is_final=True,
            )

        logger.info(f"STT transcript processed: '{cleaned}' ({lang_code})")
        return STTResult(
            transcript=cleaned,
            confidence=0.9,  # Web Speech API doesn't expose confidence per-result
            provider_used=STTProvider.BROWSER,
            language=lang_code,
            is_final=True,
        )

    def get_supported_languages(self) -> dict:
        """Return all supported STT language codes."""
        return BROWSER_LANG_MAP


# Global singleton instance
stt_engine = STTEngine()
