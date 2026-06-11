"""
SignBridge AI — Layer 5: Google Translate Adapter
HTTP-based adapter for Google Translate's unofficial endpoint.
Uses httpx (already installed) with no API key requirement.
Falls back gracefully on network errors.
"""

import httpx

from config.logger import setup_logger
from translation.providers.base import BaseTranslationProvider
from translation.providers.rule_based import RuleBasedProvider

logger = setup_logger("translation.providers.google_adapter")

# Language name → Google Translate BCP-47 code
GOOGLE_LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
    "Korean": "ko",
    "Bengali": "bn",
    "Tamil": "ta",
    "Urdu": "ur",
}


class GoogleTranslateAdapter(BaseTranslationProvider):
    """
    Google Translate adapter using the public translate.googleapis.com endpoint.
    Requires internet access. Falls back to RuleBasedProvider on any network error.
    No API key required for this endpoint (rate-limited, suitable for demo scale).
    """

    GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, timeout_seconds: float = 5.0):
        self._timeout = timeout_seconds
        self._fallback = RuleBasedProvider()
        self._available: bool | None = None

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def supports_multilingual(self) -> bool:
        return True

    def health_check(self) -> bool:
        """Ping Google Translate to verify connectivity."""
        try:
            resp = httpx.get(
                self.GOOGLE_TRANSLATE_URL,
                params={
                    "client": "gtx",
                    "sl": "en",
                    "tl": "es",
                    "dt": "t",
                    "q": "hello",
                },
                timeout=3.0,
            )
            self._available = resp.status_code == 200
        except Exception:
            self._available = False
        return self._available

    def signs_to_english(
        self, tokens: list[str], context: list[str] | None = None
    ) -> str:
        """
        Convert sign tokens to English.
        Delegates to RuleBasedProvider for the grammar construction phase,
        then optionally refines via Google if available.
        """
        # Grammar construction is purely local (rule-based)
        return self._fallback.signs_to_english(tokens, context)

    def translate_to_language(self, english_text: str, target_language: str) -> str:
        """
        Translate English text to target language using Google Translate API.
        Falls back to RuleBasedProvider if Google is unavailable.
        """
        if target_language == "English":
            return english_text

        lang_code = GOOGLE_LANG_CODES.get(target_language)
        if not lang_code:
            logger.warning(
                f"Unknown language '{target_language}' — falling back to rule-based."
            )
            return self._fallback.translate_to_language(english_text, target_language)

        try:
            resp = httpx.get(
                self.GOOGLE_TRANSLATE_URL,
                params={
                    "client": "gtx",
                    "sl": "en",
                    "tl": lang_code,
                    "dt": "t",
                    "q": english_text,
                },
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()

            # Parse Google's response format: [[["translated","original",...], ...], ...]
            translated_parts = []
            for item in data[0]:
                if item and item[0]:
                    translated_parts.append(item[0])

            result = "".join(translated_parts).strip()
            if result:
                logger.debug(
                    f"Google Translate: '{english_text}' → '{result}' ({target_language})"
                )
                return result

        except httpx.TimeoutException:
            logger.warning(
                f"Google Translate timeout for '{english_text}' → {target_language}. Using fallback."
            )
        except httpx.NetworkError:
            logger.warning("Google Translate network error. Using fallback.")
        except (KeyError, IndexError, ValueError) as parse_err:
            logger.error(f"Google Translate parse error: {parse_err}. Using fallback.")
        except Exception as exc:
            logger.error(f"Unexpected Google Translate error: {exc}. Using fallback.")

        return self._fallback.translate_to_language(english_text, target_language)
