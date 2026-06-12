"""
SignBridge AI — Layer 11: Locale Formatter
Formats numbers, dates, and times according to locale conventions
for each of the 16 supported languages.
"""

from datetime import datetime

from config.logger import setup_logger
from multilingual.language_registry import LANGUAGE_REGISTRY

logger = setup_logger("multilingual.locale_formatter")


class LocaleFormatter:
    """
    Locale-aware formatter for numbers, dates, and timestamps.
    Uses the Language Registry to apply correct separators and formats.
    """

    def format_number(self, value: float, language_name: str, decimal_places: int = 2) -> str:
        """
        Format a number according to the locale conventions of a language.

        Args:
            value: Number to format
            language_name: Target language
            decimal_places: Number of decimal places

        Returns:
            Locale-formatted number string
        """
        lang = LANGUAGE_REGISTRY.get(language_name)
        if not lang:
            return f"{value:.{decimal_places}f}"

        dec_sep = lang.decimal_sep
        thou_sep = lang.thousands_sep

        # Format with standard separators then replace
        formatted = f"{abs(value):,.{decimal_places}f}"
        # Replace standard separators with locale ones
        # Use placeholder to avoid double-replacement
        formatted = formatted.replace(",", "THOU").replace(".", "DEC")
        formatted = formatted.replace("THOU", thou_sep).replace("DEC", dec_sep)

        if value < 0:
            formatted = f"-{formatted}"
        return formatted

    def format_confidence(self, confidence: float, language_name: str) -> str:
        """
        Format a confidence score as a percentage in the locale format.

        Args:
            confidence: Score 0.0–1.0
            language_name: Target language

        Returns:
            Percentage string (e.g. '92,5%' for German)
        """
        percentage = confidence * 100
        formatted_num = self.format_number(percentage, language_name, decimal_places=1)
        return f"{formatted_num}%"

    def format_date(self, dt: datetime, language_name: str) -> str:
        """
        Format a datetime according to locale date format.

        Args:
            dt: Datetime object to format
            language_name: Target language

        Returns:
            Locale-formatted date string
        """
        lang = LANGUAGE_REGISTRY.get(language_name)
        if not lang:
            return dt.strftime("%Y-%m-%d")

        try:
            return dt.strftime(lang.date_format)
        except Exception:
            return dt.strftime("%Y-%m-%d")

    def format_duration(self, seconds: float, language_name: str) -> str:
        """
        Format a duration in seconds as a human-readable string.
        Outputs in English regardless of language (universal notation).

        Args:
            seconds: Duration in seconds
            language_name: Target language (for number formatting)

        Returns:
            Duration string (e.g. '2m 34s')
        """
        minutes = int(seconds // 60)
        remaining_secs = int(seconds % 60)
        if minutes > 0:
            return f"{minutes}m {remaining_secs}s"
        return f"{remaining_secs}s"

    def get_ui_strings(self, language_name: str) -> dict:
        """
        Return a dict of common UI strings translated for the given language.
        These are static strings used in the UI (button labels, headings, etc.)
        that don't go through the full translation engine.

        Args:
            language_name: Target language

        Returns:
            Dict of ui_key → translated string
        """
        UI_STRINGS = {
            "English": {
                "start": "Start",
                "stop": "Stop",
                "reset": "Reset",
                "save": "Save",
                "loading": "Loading...",
            },
            "Hindi": {
                "start": "शुरू करें",
                "stop": "रोकें",
                "reset": "रीसेट",
                "save": "सहेजें",
                "loading": "लोड हो रहा है...",
            },
            "Telugu": {
                "start": "ప్రారంభించు",
                "stop": "ఆపు",
                "reset": "రీసెట్",
                "save": "సేవ్ చేయి",
                "loading": "లోడ్ అవుతోంది...",
            },
            "Spanish": {
                "start": "Iniciar",
                "stop": "Detener",
                "reset": "Restablecer",
                "save": "Guardar",
                "loading": "Cargando...",
            },
            "French": {
                "start": "Démarrer",
                "stop": "Arrêter",
                "reset": "Réinitialiser",
                "save": "Sauvegarder",
                "loading": "Chargement...",
            },
            "German": {
                "start": "Starten",
                "stop": "Stoppen",
                "reset": "Zurücksetzen",
                "save": "Speichern",
                "loading": "Laden...",
            },
            "Chinese": {
                "start": "开始",
                "stop": "停止",
                "reset": "重置",
                "save": "保存",
                "loading": "加载中...",
            },
            "Japanese": {
                "start": "開始",
                "stop": "停止",
                "reset": "リセット",
                "save": "保存",
                "loading": "読み込み中...",
            },
            "Arabic": {
                "start": "بدء",
                "stop": "إيقاف",
                "reset": "إعادة تعيين",
                "save": "حفظ",
                "loading": "جار التحميل...",
            },
            "Portuguese": {
                "start": "Iniciar",
                "stop": "Parar",
                "reset": "Redefinir",
                "save": "Salvar",
                "loading": "Carregando...",
            },
            "Russian": {
                "start": "Начать",
                "stop": "Стоп",
                "reset": "Сбросить",
                "save": "Сохранить",
                "loading": "Загрузка...",
            },
            "Italian": {
                "start": "Avvia",
                "stop": "Ferma",
                "reset": "Reimposta",
                "save": "Salva",
                "loading": "Caricamento...",
            },
            "Korean": {
                "start": "시작",
                "stop": "중지",
                "reset": "초기화",
                "save": "저장",
                "loading": "로드 중...",
            },
            "Bengali": {
                "start": "শুরু করুন",
                "stop": "বন্ধ করুন",
                "reset": "রিসেট",
                "save": "সংরক্ষণ",
                "loading": "লোড হচ্ছে...",
            },
            "Tamil": {
                "start": "தொடங்கு",
                "stop": "நிறுத்து",
                "reset": "மீட்டமை",
                "save": "சேமி",
                "loading": "ஏற்றுகிறது...",
            },
            "Urdu": {
                "start": "شروع کریں",
                "stop": "روکیں",
                "reset": "دوبارہ ترتیب دیں",
                "save": "محفوظ کریں",
                "loading": "لوڈ ہو رہا ہے...",
            },
        }
        return UI_STRINGS.get(language_name, UI_STRINGS["English"])


locale_formatter = LocaleFormatter()
