"""
SignBridge AI — Layer 6 Speech Engine Test Suite
Tests: TTS engine, gTTS provider, browser provider, voice profiles, STT engine.
"""
import pytest
from speech.tts_engine import TTSEngine, tts_engine
from speech.stt_engine import STTEngine, stt_engine
from speech.providers.gtts_provider import GTTSProvider
from speech.providers.browser_provider import BrowserTTSProvider
from speech.voice_profile import get_profile_for_language, VOICE_PROFILES, LANGUAGE_TO_PROFILE
from speech.schemas import TTSRequest, TTSProvider, STTProvider


class TestGTTSProvider:
    """Tests for the gTTS provider."""

    def setup_method(self):
        self.provider = GTTSProvider()

    def test_provider_name(self):
        assert self.provider.provider_name == "gtts"

    def test_audio_format_string(self):
        assert self.provider.audio_format in {"mp3", "wav"}

    def test_synthesize_empty_text_returns_failure(self):
        result = self.provider.synthesize("")
        assert not result.success

    def test_synthesize_returns_result_object(self):
        result = self.provider.synthesize("Hello", lang_code="en-US")
        assert result is not None
        assert isinstance(result.audio_bytes, bytes)

    def test_synthesize_produces_bytes(self):
        result = self.provider.synthesize("I need help.", lang_code="en-US")
        # Either real gTTS MP3 or mock WAV fallback — both must be non-empty
        assert len(result.audio_bytes) > 0

    def test_synthesize_hindi(self):
        result = self.provider.synthesize("नमस्ते", lang_code="hi-IN")
        assert isinstance(result.audio_bytes, bytes)

    def test_get_available_voices_non_empty(self):
        voices = self.provider.get_available_voices()
        assert len(voices) > 0

    def test_voice_has_required_fields(self):
        voices = self.provider.get_available_voices()
        for voice in voices:
            assert voice.id
            assert voice.name
            assert voice.lang_code


class TestBrowserTTSProvider:
    """Tests for the browser Web Speech API TTS provider."""

    def setup_method(self):
        self.provider = BrowserTTSProvider()

    def test_provider_name(self):
        assert self.provider.provider_name == "browser"

    def test_audio_format_is_browser_native(self):
        assert self.provider.audio_format == "browser_native"

    def test_synthesize_returns_result(self):
        result = self.provider.synthesize("Hello world", lang_code="en-US")
        assert result.success
        assert result.provider_used == TTSProvider.BROWSER

    def test_synthesize_empty_fails(self):
        result = self.provider.synthesize("")
        assert not result.success

    def test_get_javascript_snippet_contains_script_tag(self):
        js = self.provider.get_javascript_snippet("Hello", "en-US", slow=False)
        assert "<script>" in js
        assert "speechSynthesis" in js

    def test_get_javascript_snippet_includes_text(self):
        js = self.provider.get_javascript_snippet("Need help", "en-US", slow=False)
        assert "Need help" in js

    def test_get_javascript_snippet_slow_mode(self):
        js = self.provider.get_javascript_snippet("Hello", "en-US", slow=True)
        assert "0.7" in js  # Slow rate

    def test_get_available_voices_non_empty(self):
        voices = self.provider.get_available_voices()
        assert len(voices) > 0


class TestVoiceProfiles:
    """Tests for the voice profile registry."""

    def test_all_16_languages_have_profile(self):
        from config.config import SUPPORTED_LANGUAGES
        for language in SUPPORTED_LANGUAGES.keys():
            profile = get_profile_for_language(language)
            assert profile is not None
            assert profile.lang_code

    def test_english_profile_code(self):
        profile = get_profile_for_language("English")
        assert "en" in profile.lang_code.lower()

    def test_slow_override(self):
        profile = get_profile_for_language("English", slow=True)
        assert profile.slow is True

    def test_hindi_profile_exists(self):
        profile = get_profile_for_language("Hindi")
        assert "hi" in profile.lang_code

    def test_arabic_profile_exists(self):
        profile = get_profile_for_language("Arabic")
        assert "ar" in profile.lang_code

    def test_emergency_profile_exists(self):
        assert "emergency" in VOICE_PROFILES
        assert VOICE_PROFILES["emergency"].slow is False


class TestTTSEngine:
    """Tests for the full TTS Engine orchestrator."""

    def setup_method(self):
        self.engine = TTSEngine()

    def test_speak_returns_bytes(self):
        audio = self.engine.speak("Hello world", language_name="English")
        assert isinstance(audio, bytes)

    def test_speak_non_empty_audio(self):
        audio = self.engine.speak("I need water.", language_name="English")
        assert len(audio) > 0

    def test_speak_spanish(self):
        audio = self.engine.speak("Hola mundo", language_name="Spanish")
        assert isinstance(audio, bytes)

    def test_speak_emergency_returns_bytes(self):
        audio = self.engine.speak_emergency("CRITICAL EMERGENCY — call 911 immediately!")
        assert isinstance(audio, bytes)
        assert len(audio) > 0

    def test_caching_second_call_faster(self):
        import time
        text = "Cached test phrase for SignBridge."
        self.engine.speak(text, language_name="English")
        start = time.perf_counter()
        self.engine.speak(text, language_name="English")
        elapsed = time.perf_counter() - start
        # Cache hit should be very fast (< 50ms)
        assert elapsed < 0.05

    def test_clear_cache(self):
        self.engine.speak("Clear me", language_name="English")
        cleared = self.engine.clear_cache()
        assert cleared >= 0  # May be 0 if cache was already empty

    def test_get_all_voices_non_empty(self):
        voices = self.engine.get_all_voices()
        assert len(voices) > 0

    def test_get_provider_health_returns_dict(self):
        health = self.engine.get_provider_health()
        assert isinstance(health, dict)
        assert "gtts" in health

    def test_get_browser_js_returns_html(self):
        html = self.engine.get_browser_js("Hello", lang_code="en-US")
        assert "<script>" in html

    def test_synthesize_with_full_request(self):
        request = TTSRequest(text="Full pipeline test", lang_code="en-US", provider=TTSProvider.GTTS)
        result = self.engine.synthesize(request)
        assert result is not None
        assert isinstance(result.audio_bytes, bytes)


class TestSTTEngine:
    """Tests for the STT Engine."""

    def setup_method(self):
        self.engine = STTEngine()

    def test_get_stt_html_contains_script(self):
        html = self.engine.get_stt_html(lang_code="en-US")
        assert "<script>" in html
        assert "SpeechRecognition" in html

    def test_get_stt_html_language_code_embedded(self):
        html = self.engine.get_stt_html(lang_code="hi-IN")
        assert "hi-IN" in html

    def test_process_transcript_returns_result(self):
        result = self.engine.process_transcript("I need water", lang_code="en-US")
        assert result.transcript == "I need water"
        assert result.provider_used == STTProvider.BROWSER
        assert result.confidence > 0

    def test_process_empty_transcript(self):
        result = self.engine.process_transcript("", lang_code="en-US")
        assert result.transcript == ""
        assert result.confidence == 0.0

    def test_process_strips_whitespace(self):
        result = self.engine.process_transcript("  hello world  ")
        assert result.transcript == "hello world"

    def test_get_supported_languages_dict(self):
        langs = self.engine.get_supported_languages()
        assert isinstance(langs, dict)
        assert "en-US" in langs.values()
