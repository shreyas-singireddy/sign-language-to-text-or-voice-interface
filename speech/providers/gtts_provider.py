"""
SignBridge AI — Layer 6: gTTS Provider
Uses Google Text-to-Speech (gTTS) library for high-quality multilingual TTS.
gTTS produces MP3 audio streamed from Google's TTS API.
Falls back to WAV mock synthesis if gTTS is not installed or offline.
"""

import io
import math
import wave

import numpy as np

from config.logger import setup_logger
from speech.providers.base import BaseTTSProvider
from speech.schemas import AvailableVoice, TTSProvider, TTSResult

logger = setup_logger("speech.providers.gtts")

# Language name → gTTS lang code + TLD for accent variation
GTTS_LANGUAGE_MAP = {
    "en": ("en", "com"),  # English (US)
    "en-US": ("en", "com"),
    "en-GB": ("en", "co.uk"),
    "en-AU": ("en", "com.au"),
    "hi-IN": ("hi", "co.in"),
    "te-IN": ("te", "co.in"),
    "es-ES": ("es", "es"),
    "fr-FR": ("fr", "fr"),
    "de-DE": ("de", "de"),
    "zh-CN": ("zh-CN", "com"),
    "ja-JP": ("ja", "com"),
    "ar-SA": ("ar", "com"),
    "pt-PT": ("pt", "com.br"),
    "ru-RU": ("ru", "com"),
    "it-IT": ("it", "it"),
    "ko-KR": ("ko", "com"),
    "bn-IN": ("bn", "com"),
    "ta-IN": ("ta", "co.in"),
    "ur-PK": ("ur", "com"),
}

# Pre-defined voice catalog for the UI
VOICE_CATALOG: list[AvailableVoice] = [
    AvailableVoice(
        id="gtts_en_us",
        name="American English",
        language="English",
        lang_code="en-US",
        provider=TTSProvider.GTTS,
        accent="US",
    ),
    AvailableVoice(
        id="gtts_en_gb",
        name="British English",
        language="English",
        lang_code="en-GB",
        provider=TTSProvider.GTTS,
        accent="UK",
    ),
    AvailableVoice(
        id="gtts_en_au",
        name="Australian English",
        language="English",
        lang_code="en-AU",
        provider=TTSProvider.GTTS,
        accent="AU",
    ),
    AvailableVoice(
        id="gtts_hi",
        name="Hindi",
        language="Hindi",
        lang_code="hi-IN",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_te",
        name="Telugu",
        language="Telugu",
        lang_code="te-IN",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_es",
        name="Spanish",
        language="Spanish",
        lang_code="es-ES",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_fr",
        name="French",
        language="French",
        lang_code="fr-FR",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_de",
        name="German",
        language="German",
        lang_code="de-DE",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_zh",
        name="Chinese Mandarin",
        language="Chinese",
        lang_code="zh-CN",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ja",
        name="Japanese",
        language="Japanese",
        lang_code="ja-JP",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ar",
        name="Arabic",
        language="Arabic",
        lang_code="ar-SA",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_pt",
        name="Portuguese",
        language="Portuguese",
        lang_code="pt-PT",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ru",
        name="Russian",
        language="Russian",
        lang_code="ru-RU",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_it",
        name="Italian",
        language="Italian",
        lang_code="it-IT",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ko",
        name="Korean",
        language="Korean",
        lang_code="ko-KR",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_bn",
        name="Bengali",
        language="Bengali",
        lang_code="bn-IN",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ta",
        name="Tamil",
        language="Tamil",
        lang_code="ta-IN",
        provider=TTSProvider.GTTS,
    ),
    AvailableVoice(
        id="gtts_ur",
        name="Urdu",
        language="Urdu",
        lang_code="ur-PK",
        provider=TTSProvider.GTTS,
    ),
]


class GTTSProvider(BaseTTSProvider):
    """
    Google Text-to-Speech provider using the gTTS library.
    Produces high-quality MP3 audio for 16+ languages.
    Gracefully falls back to sine-wave mock audio if gTTS is unavailable.
    """

    def __init__(self):
        self._gtts_available = self._check_gtts()

    def _check_gtts(self) -> bool:
        """Check if gTTS library is installed and importable."""
        try:
            import gtts  # noqa: F401

            logger.info("gTTS library detected and available.")
            return True
        except ImportError:
            logger.warning(
                "gTTS not installed. Run: pip install gTTS. Using mock WAV fallback."
            )
            return False

    @property
    def provider_name(self) -> str:
        return "gtts"

    @property
    def audio_format(self) -> str:
        return "mp3" if self._gtts_available else "wav"

    def health_check(self) -> bool:
        return self._gtts_available

    def synthesize(
        self, text: str, lang_code: str = "en", slow: bool = False, tld: str = "com"
    ) -> TTSResult:
        """
        Synthesize text into audio using gTTS if available, otherwise WAV mock.
        """
        if not text.strip():
            return TTSResult(
                audio_bytes=b"",
                format="mp3",
                provider_used=TTSProvider.GTTS,
                text_synthesized=text,
                lang_code=lang_code,
                success=False,
                error="Empty text provided",
            )

        # Resolve language code
        lang, resolved_tld = GTTS_LANGUAGE_MAP.get(lang_code, ("en", "com"))
        if tld != "com":
            resolved_tld = tld

        if self._gtts_available:
            return self._synthesize_gtts(text, lang, slow, resolved_tld)
        else:
            return self._synthesize_mock_wav(text, lang_code)

    def _synthesize_gtts(self, text: str, lang: str, slow: bool, tld: str) -> TTSResult:
        """Use gTTS to produce real MP3 audio."""
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang=lang, slow=slow, tld=tld)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            audio_bytes = buffer.read()

            # Estimate duration: ~150 words/minute at normal speed, ~75 at slow
            word_count = len(text.split())
            wpm = 75 if slow else 150
            duration = (word_count / wpm) * 60

            logger.info(
                f"gTTS synthesized {len(audio_bytes)} bytes for lang={lang}: '{text[:60]}'"
            )
            return TTSResult(
                audio_bytes=audio_bytes,
                format="mp3",
                provider_used=TTSProvider.GTTS,
                text_synthesized=text,
                lang_code=lang,
                duration_estimate_seconds=round(duration, 1),
                success=True,
            )
        except Exception as exc:
            logger.error(f"gTTS synthesis failed: {exc}. Falling back to mock.")
            return self._synthesize_mock_wav(text, lang)

    def _synthesize_mock_wav(self, text: str, lang_code: str) -> TTSResult:
        """
        Generate a multi-tone WAV audio file as offline fallback.
        Produces a pleasant ascending chord proportional to text length.
        """
        sample_rate = 22050
        word_count = max(len(text.split()), 1)
        duration = max(0.5, min(word_count * 0.4, 8.0))  # 0.4s per word, max 8s
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # Generate a triad chord (tonic, major third, perfect fifth)
        base_freq = 261.63  # Middle C
        wave_data = (
            0.5 * np.sin(2 * math.pi * base_freq * t)
            + 0.3 * np.sin(2 * math.pi * base_freq * 1.25 * t)
            + 0.2 * np.sin(2 * math.pi * base_freq * 1.5 * t)
        )

        # Apply envelope (fade in + fade out)
        fade_samples = int(sample_rate * 0.05)
        if len(wave_data) > 2 * fade_samples:
            wave_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
            wave_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        audio_ints = np.int16(wave_data * 32767)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_ints.tobytes())

        logger.info(f"Mock WAV generated ({duration:.1f}s) for: '{text[:60]}'")
        return TTSResult(
            audio_bytes=wav_buffer.getvalue(),
            format="wav",
            provider_used=TTSProvider.MOCK,
            text_synthesized=text,
            lang_code=lang_code,
            duration_estimate_seconds=round(duration, 1),
            success=True,
        )

    def get_available_voices(self) -> list[AvailableVoice]:
        return VOICE_CATALOG
