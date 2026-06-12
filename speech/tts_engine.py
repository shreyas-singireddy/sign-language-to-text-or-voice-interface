"""
SignBridge AI — Layer 6: TTS Engine
Orchestrates text-to-speech synthesis across multiple providers.
Primary: gTTS (Google TTS, internet-dependent, high quality)
Secondary: Browser (Web Speech API, on-device, zero-latency)
Fallback: Mock WAV sine wave (always available offline)

Caches audio bytes per text+language key to avoid redundant synthesis.
"""

import hashlib

from config.logger import setup_logger
from speech.providers.browser_provider import BrowserTTSProvider
from speech.providers.gtts_provider import GTTSProvider
from speech.schemas import AvailableVoice, TTSProvider, TTSRequest, TTSResult
from speech.voice_profile import get_profile_for_language

logger = setup_logger("speech.tts_engine")

# Maximum number of cached TTS results
CACHE_MAX_SIZE = 100


class TTSEngine:
    """
    Layer 6 Text-to-Speech Engine.
    Orchestrates provider selection, audio synthesis, and caching.

    Usage:
        result = tts_engine.synthesize(text="Hello!", lang_code="en-US")
        st.audio(result.audio_bytes, format=result.format)

    Or using simple interface:
        audio_bytes = tts_engine.speak(text="Hello", language_name="English")
    """

    def __init__(self):
        self._providers: dict[TTSProvider, object] = {
            TTSProvider.GTTS: GTTSProvider(),
            TTSProvider.BROWSER: BrowserTTSProvider(),
        }
        self._cache: dict[str, TTSResult] = {}
        self._default_provider = TTSProvider.GTTS
        logger.info("TTSEngine initialized with providers: gtts, browser")

    def synthesize(self, request: TTSRequest) -> TTSResult:
        """
        Synthesize speech from a TTSRequest.

        Args:
            request: Full TTS request with text, language, and provider

        Returns:
            TTSResult with audio bytes and metadata
        """
        cache_key = self._make_cache_key(request.text, request.lang_code, request.slow)

        # Return cached result if available
        if cache_key in self._cache:
            logger.debug(f"Cache hit for TTS: '{request.text[:40]}'")
            return self._cache[cache_key]

        # Select provider
        provider = self._providers.get(request.provider, self._providers[self._default_provider])

        # Execute synthesis
        result = provider.synthesize(
            text=request.text,
            lang_code=request.lang_code,
            slow=request.slow,
            tld=request.tld,
        )

        # Cache successful results
        if result.success and result.audio_bytes:
            self._store_cache(cache_key, result)

        return result

    def speak(
        self,
        text: str,
        language_name: str = "English",
        slow: bool = False,
        provider: TTSProvider = TTSProvider.GTTS,
    ) -> bytes:
        """
        Simplified interface — returns raw audio bytes directly.
        Ideal for Streamlit page calls: st.audio(tts_engine.speak(text, "Hindi"))

        Args:
            text: Text to synthesize
            language_name: Language display name (e.g. 'Hindi', 'Spanish')
            slow: Use slow speech rate for accessibility
            provider: TTS provider to use

        Returns:
            Raw audio bytes (MP3 or WAV depending on provider)
        """
        profile = get_profile_for_language(language_name, slow=slow)
        request = TTSRequest(
            text=text,
            lang_code=profile.lang_code,
            provider=provider,
            slow=profile.slow,
            tld=profile.tld,
        )
        result = self.synthesize(request)
        return result.audio_bytes

    def speak_emergency(self, text: str) -> bytes:
        """
        Synthesize emergency text with high priority.
        Always uses English regardless of session language.
        Bypasses cache.

        Args:
            text: Emergency message text

        Returns:
            Raw MP3/WAV audio bytes
        """
        TTSRequest(
            text=text,
            lang_code="en-US",
            provider=TTSProvider.GTTS,
            slow=False,
            tld="com",
        )
        provider = self._providers[TTSProvider.GTTS]
        result = provider.synthesize(text=text, lang_code="en-US", slow=False, tld="com")
        logger.warning(f"Emergency TTS synthesized: '{text[:80]}'")
        return result.audio_bytes

    def get_browser_js(self, text: str, lang_code: str = "en-US", slow: bool = False) -> str:
        """
        Get JavaScript snippet for browser-native TTS playback.
        Use with: st.components.v1.html(tts_engine.get_browser_js(text))

        Args:
            text: Text for browser to speak
            lang_code: BCP-47 language code
            slow: Use slow rate

        Returns:
            HTML string with embedded <script> tag
        """
        browser_provider: BrowserTTSProvider = self._providers[TTSProvider.BROWSER]
        return browser_provider.get_javascript_snippet(text, lang_code, slow)

    def get_all_voices(self) -> list[AvailableVoice]:
        """Return combined voice list from all providers."""
        voices = []
        for provider in self._providers.values():
            if hasattr(provider, "get_available_voices"):
                voices.extend(provider.get_available_voices())
        return voices

    def get_provider_health(self) -> dict[str, bool]:
        """Return health status for all providers."""
        return {name.value: provider.health_check() for name, provider in self._providers.items()}

    def clear_cache(self) -> int:
        """Clear the audio cache. Returns number of entries cleared."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"TTS cache cleared ({count} entries).")
        return count

    def _make_cache_key(self, text: str, lang_code: str, slow: bool) -> str:
        """Generate a deterministic cache key from synthesis parameters."""
        content = f"{text}|{lang_code}|{slow}"
        return hashlib.md5(content.encode()).hexdigest()  # nosec

    def _store_cache(self, key: str, result: TTSResult) -> None:
        """Store result in cache with LRU eviction if full."""
        if len(self._cache) >= CACHE_MAX_SIZE:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = result

    def get_audio_format(self, provider: TTSProvider = TTSProvider.GTTS) -> str:
        """Return the audio format for a given provider."""
        provider_obj = self._providers.get(provider)
        if provider_obj and hasattr(provider_obj, "audio_format"):
            return provider_obj.audio_format
        return "wav"


# Global singleton instance
tts_engine = TTSEngine()
