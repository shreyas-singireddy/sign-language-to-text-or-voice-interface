"""
SignBridge AI — Translation Configuration Registry
Defines the metadata mapping for the 12 supported Indian languages.
"""

from dataclasses import dataclass


@dataclass
class LanguageMetadata:
    code: str
    name: str
    native_name: str
    bcp47: str
    tts_code: str
    is_rtl: bool = False
    flag: str = "🌐"


# Supported Languages Configuration Registry
SUPPORTED_LANGUAGES: dict[str, LanguageMetadata] = {
    "English": LanguageMetadata(
        code="en",
        name="English",
        native_name="English",
        bcp47="en-US",
        tts_code="en",
        flag="🇺🇸",
    ),
    "Spanish": LanguageMetadata(
        code="es",
        name="Spanish",
        native_name="Español",
        bcp47="es-ES",
        tts_code="es",
        flag="🇪🇸",
    ),
    "Hindi": LanguageMetadata(
        code="hi",
        name="Hindi",
        native_name="हिंदी",
        bcp47="hi-IN",
        tts_code="hi",
        flag="🇮🇳",
    ),
    "Telugu": LanguageMetadata(
        code="te",
        name="Telugu",
        native_name="తెలుగు",
        bcp47="te-IN",
        tts_code="te",
        flag="🇮🇳",
    ),
    "Tamil": LanguageMetadata(
        code="ta",
        name="Tamil",
        native_name="தமிழ்",
        bcp47="ta-IN",
        tts_code="ta",
        flag="🇮🇳",
    ),
    "Kannada": LanguageMetadata(
        code="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        bcp47="kn-IN",
        tts_code="kn",
        flag="🇮🇳",
    ),
    "Malayalam": LanguageMetadata(
        code="ml",
        name="Malayalam",
        native_name="മലയാളം",
        bcp47="ml-IN",
        tts_code="ml",
        flag="🇮🇳",
    ),
    "Marathi": LanguageMetadata(
        code="mr",
        name="Marathi",
        native_name="मराठी",
        bcp47="mr-IN",
        tts_code="mr",
        flag="🇮🇳",
    ),
    "Bengali": LanguageMetadata(
        code="bn",
        name="Bengali",
        native_name="বাংলা",
        bcp47="bn-IN",
        tts_code="bn",
        flag="🇮🇳",
    ),
    "Gujarati": LanguageMetadata(
        code="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        bcp47="gu-IN",
        tts_code="gu",
        flag="🇮🇳",
    ),
    "Punjabi": LanguageMetadata(
        code="pa",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        bcp47="pa-IN",
        tts_code="pa",
        flag="🇮🇳",
    ),
    "Odia": LanguageMetadata(
        code="or",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        bcp47="or-IN",
        tts_code="or",
        flag="🇮🇳",
    ),
    "Assamese": LanguageMetadata(
        code="as",
        name="Assamese",
        native_name="অসমীয়া",
        bcp47="as-IN",
        tts_code="as",
        flag="🇮🇳",
    ),
    "Portuguese": LanguageMetadata(
        code="pt",
        name="Portuguese",
        native_name="Português",
        bcp47="pt-PT",
        tts_code="pt",
        flag="🇵🇹",
    ),
}


def get_language_by_code(code: str) -> LanguageMetadata | None:
    """Retrieve language metadata using its 2-letter language code."""
    for lang in SUPPORTED_LANGUAGES.values():
        if lang.code == code:
            return lang
    return None


def get_language_by_name(name: str) -> LanguageMetadata | None:
    """Retrieve language metadata using its display name."""
    return SUPPORTED_LANGUAGES.get(name)
