"""
SignBridge AI — Layer 11: Language Registry
Central registry for all 16 supported languages with metadata:
BCP-47 codes, script, RTL flag, native name, flag emoji, and locale info.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from config.logger import setup_logger

logger = setup_logger("multilingual.language_registry")


@dataclass
class Language:
    """Complete metadata for a supported language."""
    name: str                   # Display name in English
    native_name: str            # Name in the native script
    bcp47: str                  # BCP-47 language tag
    tts_code: str               # Language code for TTS (gTTS)
    script: str                 # Script name (Latin, Devanagari, etc.)
    is_rtl: bool                # Right-to-left text direction
    flag: str                   # Country flag emoji
    region: str                 # Geographic region
    decimal_sep: str            # Decimal separator character
    thousands_sep: str          # Thousands separator character
    date_format: str            # strftime date format pattern


# Complete 16-language registry
LANGUAGE_REGISTRY: Dict[str, Language] = {
    "English": Language(
        name="English", native_name="English", bcp47="en-US", tts_code="en",
        script="Latin", is_rtl=False, flag="🇺🇸", region="Americas",
        decimal_sep=".", thousands_sep=",", date_format="%m/%d/%Y",
    ),
    "Hindi": Language(
        name="Hindi", native_name="हिंदी", bcp47="hi-IN", tts_code="hi",
        script="Devanagari", is_rtl=False, flag="🇮🇳", region="South Asia",
        decimal_sep=".", thousands_sep=",", date_format="%d/%m/%Y",
    ),
    "Telugu": Language(
        name="Telugu", native_name="తెలుగు", bcp47="te-IN", tts_code="te",
        script="Telugu", is_rtl=False, flag="🇮🇳", region="South Asia",
        decimal_sep=".", thousands_sep=",", date_format="%d/%m/%Y",
    ),
    "Spanish": Language(
        name="Spanish", native_name="Español", bcp47="es-ES", tts_code="es",
        script="Latin", is_rtl=False, flag="🇪🇸", region="Europe",
        decimal_sep=",", thousands_sep=".", date_format="%d/%m/%Y",
    ),
    "French": Language(
        name="French", native_name="Français", bcp47="fr-FR", tts_code="fr",
        script="Latin", is_rtl=False, flag="🇫🇷", region="Europe",
        decimal_sep=",", thousands_sep=" ", date_format="%d/%m/%Y",
    ),
    "German": Language(
        name="German", native_name="Deutsch", bcp47="de-DE", tts_code="de",
        script="Latin", is_rtl=False, flag="🇩🇪", region="Europe",
        decimal_sep=",", thousands_sep=".", date_format="%d.%m.%Y",
    ),
    "Chinese": Language(
        name="Chinese", native_name="中文", bcp47="zh-CN", tts_code="zh-CN",
        script="Han", is_rtl=False, flag="🇨🇳", region="East Asia",
        decimal_sep=".", thousands_sep=",", date_format="%Y年%m月%d日",
    ),
    "Japanese": Language(
        name="Japanese", native_name="日本語", bcp47="ja-JP", tts_code="ja",
        script="Japanese", is_rtl=False, flag="🇯🇵", region="East Asia",
        decimal_sep=".", thousands_sep=",", date_format="%Y年%m月%d日",
    ),
    "Arabic": Language(
        name="Arabic", native_name="العربية", bcp47="ar-SA", tts_code="ar",
        script="Arabic", is_rtl=True, flag="🇸🇦", region="Middle East",
        decimal_sep="٫", thousands_sep="٬", date_format="%d/%m/%Y",
    ),
    "Portuguese": Language(
        name="Portuguese", native_name="Português", bcp47="pt-BR", tts_code="pt",
        script="Latin", is_rtl=False, flag="🇧🇷", region="Americas",
        decimal_sep=",", thousands_sep=".", date_format="%d/%m/%Y",
    ),
    "Russian": Language(
        name="Russian", native_name="Русский", bcp47="ru-RU", tts_code="ru",
        script="Cyrillic", is_rtl=False, flag="🇷🇺", region="Europe",
        decimal_sep=",", thousands_sep=" ", date_format="%d.%m.%Y",
    ),
    "Italian": Language(
        name="Italian", native_name="Italiano", bcp47="it-IT", tts_code="it",
        script="Latin", is_rtl=False, flag="🇮🇹", region="Europe",
        decimal_sep=",", thousands_sep=".", date_format="%d/%m/%Y",
    ),
    "Korean": Language(
        name="Korean", native_name="한국어", bcp47="ko-KR", tts_code="ko",
        script="Hangul", is_rtl=False, flag="🇰🇷", region="East Asia",
        decimal_sep=".", thousands_sep=",", date_format="%Y년 %m월 %d일",
    ),
    "Bengali": Language(
        name="Bengali", native_name="বাংলা", bcp47="bn-IN", tts_code="bn",
        script="Bengali", is_rtl=False, flag="🇧🇩", region="South Asia",
        decimal_sep=".", thousands_sep=",", date_format="%d/%m/%Y",
    ),
    "Tamil": Language(
        name="Tamil", native_name="தமிழ்", bcp47="ta-IN", tts_code="ta",
        script="Tamil", is_rtl=False, flag="🇮🇳", region="South Asia",
        decimal_sep=".", thousands_sep=",", date_format="%d/%m/%Y",
    ),
    "Urdu": Language(
        name="Urdu", native_name="اردو", bcp47="ur-PK", tts_code="ur",
        script="Arabic", is_rtl=True, flag="🇵🇰", region="South Asia",
        decimal_sep=".", thousands_sep=",", date_format="%d/%m/%Y",
    ),
}


class LanguageRegistry:
    """
    Central access point for all language metadata in SignBridge AI.
    """

    def get(self, language_name: str) -> Optional[Language]:
        """
        Retrieve language metadata by display name.

        Args:
            language_name: Display name (e.g. 'Hindi')

        Returns:
            Language object or None if not found
        """
        return LANGUAGE_REGISTRY.get(language_name)

    def get_all(self) -> Dict[str, Language]:
        """Return the complete language registry."""
        return LANGUAGE_REGISTRY

    def get_names(self) -> List[str]:
        """Return list of all language display names."""
        return list(LANGUAGE_REGISTRY.keys())

    def get_rtl_languages(self) -> List[str]:
        """Return list of RTL language names."""
        return [name for name, lang in LANGUAGE_REGISTRY.items() if lang.is_rtl]

    def get_languages_by_region(self, region: str) -> List[str]:
        """Return languages in a specific geographic region."""
        return [name for name, lang in LANGUAGE_REGISTRY.items() if lang.region == region]

    def get_bcp47(self, language_name: str) -> str:
        """Get BCP-47 code for a language name."""
        lang = self.get(language_name)
        return lang.bcp47 if lang else "en-US"

    def get_tts_code(self, language_name: str) -> str:
        """Get TTS engine code for a language name."""
        lang = self.get(language_name)
        return lang.tts_code if lang else "en"

    def is_rtl(self, language_name: str) -> bool:
        """Check if a language uses RTL text direction."""
        lang = self.get(language_name)
        return lang.is_rtl if lang else False

    def get_flag(self, language_name: str) -> str:
        """Get the flag emoji for a language."""
        lang = self.get(language_name)
        return lang.flag if lang else "🌐"

    def get_native_name(self, language_name: str) -> str:
        """Get the native-script name for a language."""
        lang = self.get(language_name)
        return lang.native_name if lang else language_name

    def get_selectbox_options(self) -> List[str]:
        """
        Get language names formatted for Streamlit selectbox display.
        Format: "🇺🇸 English — English"
        """
        options = []
        for name, lang in LANGUAGE_REGISTRY.items():
            options.append(f"{lang.flag} {name} — {lang.native_name}")
        return options


language_registry = LanguageRegistry()
