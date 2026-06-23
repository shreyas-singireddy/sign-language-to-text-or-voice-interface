import json
from pathlib import Path

from config.logger import setup_logger

logger = setup_logger("app.utils.i18n")


class I18nEngine:
    """
    Internationalization (i18n) Engine
    Loads locale JSON files and provides translation lookups based on current language.
    """

    def __init__(self, locales_dir: str = "locales", default_lang: str = "en"):
        self.locales_dir = Path(__file__).resolve().parent.parent.parent / locales_dir
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.translations: dict[str, dict[str, str]] = {}

        self._load_all_locales()

    def _load_all_locales(self):
        """Loads all .json files from the locales directory into memory."""
        if not self.locales_dir.exists():
            logger.error(f"Locales directory not found: {self.locales_dir}")
            return

        for filepath in self.locales_dir.glob("*.json"):
            lang_code = filepath.stem
            try:
                with open(filepath, encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)
                logger.debug(f"Loaded locale: {lang_code}")
            except Exception as e:
                logger.error(f"Failed to load locale {filepath}: {e}")

    def set_language(self, lang_code: str):
        """Sets the active language for the engine."""
        # Map full language names from frontend to lang codes
        lang_map = {"English": "en", "Hindi": "hi", "Telugu": "te"}
        mapped_code = lang_map.get(lang_code, lang_code)

        if mapped_code in self.translations:
            self.current_lang = mapped_code
            logger.info(f"Language set to: {mapped_code}")
        else:
            logger.warning(f"Language '{mapped_code}' not found. Falling back to {self.default_lang}.")
            self.current_lang = self.default_lang

    def t(self, key: str, **kwargs) -> str:
        """
        Translates a key into the current language.
        Falls back to English, then to the key itself if not found.
        """
        # Try current language
        if self.current_lang in self.translations and key in self.translations[self.current_lang]:
            text = self.translations[self.current_lang][key]
        # Fallback to default
        elif self.default_lang in self.translations and key in self.translations[self.default_lang]:
            text = self.translations[self.default_lang][key]
        # Return key if completely missing
        else:
            text = key

        # Format variables if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass

        return text


# Singleton instance
i18n = I18nEngine()
