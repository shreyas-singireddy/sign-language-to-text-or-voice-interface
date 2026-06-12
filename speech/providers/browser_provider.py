"""
SignBridge AI — Layer 6: Browser TTS Provider
Bridges Streamlit's Python backend to the browser's native Web Speech API
via injected JavaScript. Enables on-device TTS with zero latency and
no external dependencies.
"""

from config.logger import setup_logger
from speech.providers.base import BaseTTSProvider
from speech.schemas import AvailableVoice, TTSProvider, TTSResult

logger = setup_logger("speech.providers.browser")

# Language name → BCP-47 codes supported by Web Speech API
BROWSER_LANG_MAP = {
    "en-US": "en-US",
    "en-GB": "en-GB",
    "en-AU": "en-AU",
    "hi-IN": "hi-IN",
    "te-IN": "te-IN",
    "es-ES": "es-ES",
    "fr-FR": "fr-FR",
    "de-DE": "de-DE",
    "zh-CN": "zh-CN",
    "ja-JP": "ja-JP",
    "ar-SA": "ar-SA",
    "pt-PT": "pt-BR",
    "ru-RU": "ru-RU",
    "it-IT": "it-IT",
    "ko-KR": "ko-KR",
    "bn-IN": "bn-IN",
    "ta-IN": "ta-IN",
    "ur-PK": "ur-PK",
    "en": "en-US",
}


class BrowserTTSProvider(BaseTTSProvider):
    """
    Browser-native Web Speech API TTS provider.
    Injects JavaScript into Streamlit to trigger speechSynthesis.speak().
    Returns a special sentinel result (no audio bytes) — audio is played
    directly in the browser tab.
    """

    @property
    def provider_name(self) -> str:
        return "browser"

    @property
    def audio_format(self) -> str:
        return "browser_native"

    def synthesize(self, text: str, lang_code: str = "en-US", slow: bool = False, tld: str = "com") -> TTSResult:
        """
        Trigger browser Web Speech API to speak text.
        Returns empty audio bytes (audio plays directly in the browser).
        """
        if not text.strip():
            return TTSResult(
                audio_bytes=b"",
                format="browser_native",
                provider_used=TTSProvider.BROWSER,
                text_synthesized=text,
                lang_code=lang_code,
                success=False,
                error="Empty text",
            )

        lang = BROWSER_LANG_MAP.get(lang_code, "en-US")
        rate = 0.7 if slow else 1.0
        logger.info(f"Browser TTS: lang={lang}, rate={rate}, text='{text[:60]}'")

        return TTSResult(
            audio_bytes=b"",  # Browser handles audio natively
            format="browser_native",
            provider_used=TTSProvider.BROWSER,
            text_synthesized=text,
            lang_code=lang,
            success=True,
        )

    def get_javascript_snippet(self, text: str, lang_code: str = "en-US", slow: bool = False) -> str:
        """
        Generate the JavaScript snippet to inject into Streamlit via st.components.v1.html().
        Call this separately to actually trigger browser TTS playback.

        Args:
            text: Text to speak aloud
            lang_code: BCP-47 language code
            slow: Whether to use slow speech rate

        Returns:
            HTML string containing the Web Speech API script
        """
        lang = BROWSER_LANG_MAP.get(lang_code, "en-US")
        rate = 0.7 if slow else 1.0
        # Escape single quotes in text
        safe_text = text.replace("'", "\\'").replace("\n", " ")

        return f"""
        <script>
        (function() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{safe_text}');
                msg.lang = '{lang}';
                msg.rate = {rate};
                msg.pitch = 1.0;
                msg.volume = 1.0;
                window.speechSynthesis.speak(msg);
            }} else {{
                console.warn('Web Speech API not supported in this browser.');
            }}
        }})();
        </script>
        """

    def get_available_voices(self) -> list[AvailableVoice]:
        """
        Returns voices exposed through Web Speech API (browser-enumerated at runtime).
        Returns a representative list for UI display.
        """
        return [
            AvailableVoice(
                id="browser_en_us",
                name="Browser English (US)",
                language="English",
                lang_code="en-US",
                provider=TTSProvider.BROWSER,
                accent="US",
            ),
            AvailableVoice(
                id="browser_en_gb",
                name="Browser English (UK)",
                language="English",
                lang_code="en-GB",
                provider=TTSProvider.BROWSER,
                accent="UK",
            ),
            AvailableVoice(
                id="browser_hi",
                name="Browser Hindi",
                language="Hindi",
                lang_code="hi-IN",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_es",
                name="Browser Spanish",
                language="Spanish",
                lang_code="es-ES",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_fr",
                name="Browser French",
                language="French",
                lang_code="fr-FR",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_de",
                name="Browser German",
                language="German",
                lang_code="de-DE",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_zh",
                name="Browser Chinese",
                language="Chinese",
                lang_code="zh-CN",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_ja",
                name="Browser Japanese",
                language="Japanese",
                lang_code="ja-JP",
                provider=TTSProvider.BROWSER,
            ),
            AvailableVoice(
                id="browser_ar",
                name="Browser Arabic",
                language="Arabic",
                lang_code="ar-SA",
                provider=TTSProvider.BROWSER,
            ),
        ]
