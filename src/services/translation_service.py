"""
SignBridge AI — Translation & Localization Service
Handles translation loaders, t() helpers, locale formatting (dates, currency),
RTL layout support, and Gemini dynamic content translation.
"""

import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any

import httpx
import streamlit as st

# Locate the project root and add it to path if needed
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.logger import setup_logger
from src.config.languages import get_language_by_name

logger = setup_logger("services.translation")

# Path to the locale JSON files
LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

# Month names dictionary for the 12 supported Indian languages
LOCALIZED_MONTHS: dict[str, list[str]] = {
    "en": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    "hi": [
        "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून",
        "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
    ],
    "te": [
        "జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్",
        "జూలై", "ఆగస్టు", "సెప్టెంబరు", "అక్టోబరు", "నవంబరు", "డిసెంబరు"
    ],
    "ta": [
        "ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்",
        "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"
    ],
    "kn": [
        "ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್",
        "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"
    ],
    "ml": [
        "ജനുവരി", "ഫെബ്രുവരി", "മാർച്ച്", "ഏപ്രിൽ", "മേയ്", "ജൂൺ",
        "ജൂലൈ", "ആഗസ്റ്റ്", "സെപ്റ്റമ്പർ", "ഒക്ടോബർ", "നവംബർ", "ഡിസംബർ"
    ],
    "mr": [
        "जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून",
        "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"
    ],
    "bn": [
        "জানুয়ারী", "ফেব্রুয়ারী", "মার্চ", "এপ্রিল", "মে", "জুন",
        "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
    ],
    "gu": [
        "જાન્યુઆરી", "ફેબ્રુઆરી", "માર્ચ", "એપ્રિલ", "મે", "જૂન",
        "જુલાઈ", "ઓગસ્ટ", "સપ્ટેમ્બર", "ઓક્ટોબર", "નવેમ્બર", "ડિસેમ્બર"
    ],
    "pa": [
        "ਜਨਵਰੀ", "ਫਰਵਰੀ", "ਮਾਰਚ", "ਅਪ੍ਰੈਲ", "ਮਈ", "ਜੂਨ",
        "ਜੁਲਾਈ", "ਅਗਸਤ", "ਸਤੰਬਰ", "ਅਕਤੂਬਰ", "ਨਵੰਬਰ", "ਦਸੰਬਰ"
    ],
    "or": [
        "ଜାନୁଆରୀ", "ଫେବୃଆରୀ", "ମାର୍ଚ୍ଚ", "ଏପ୍ରିଲ୍", "ମଇ", "ଜୁନ୍",
        "ଜୁଲାଇ", "ଅଗଷ୍ଟ", "ସେପ୍ଟେମ୍ବର", "ଅକ୍ଟୋବର", "ନଭେମ୍ବର", "ଡିସେମ୍ବର"
    ],
    "as": [
        "জানুৱাৰী", "ফেব্ৰুৱাৰী", "মাৰ্চ", "এপ্ৰিল", "মে’", "জুন",
        "জুলাই", "আগষ্ট", "ছেপ্টেম্বৰ", "অক্টোবৰ", "নৱেম্বৰ", "ডিচেম্বৰ"
    ],
}


@st.cache_data(show_spinner=False)
def load_language(lang_code: str) -> dict[str, str]:
    """
    Loads translation key-value mappings from the corresponding JSON locale file.
    Caches results using Streamlit's cache_data.
    """
    file_path = LOCALES_DIR / f"{lang_code}.json"
    if not file_path.exists():
        logger.warning(f"Locale file for '{lang_code}' not found at {file_path}. Using empty fallback.")
        return {}

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading locale file {file_path}: {e}")
        return {}


def t(key: str, **kwargs: Any) -> str:
    """
    Translation helper function. Fetches the active language translation for a key.
    Falls back to English if the key is missing in the target language.
    """
    # Determine active language from Streamlit session state
    lang_name = st.session_state.get("language", "English")
    lang_meta = get_language_by_name(lang_name)
    lang_code = lang_meta.code if lang_meta else "en"

    # Load target language translations
    translations = load_language(lang_code)

    # Lookup key in active translations
    val = translations.get(key)

    # Fallback to English
    if val is None:
        if lang_code != "en":
            en_translations = load_language("en")
            val = en_translations.get(key)

    # Fallback to the key itself
    if val is None:
        logger.warning(f"Missing translation key: '{key}'")
        val = key

    # Format values if arguments are passed
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception as e:
            logger.error(f"String format error for key '{key}' with args {kwargs}: {e}")
            return val

    return val


def format_date(dt: datetime.datetime | datetime.date, lang_name: str = None) -> str:
    """
    Format a date according to the locale conventions of the selected language.
    Example: 12 June 2026 / 12 जून 2026
    """
    if lang_name is None:
        lang_name = st.session_state.get("language", "English")

    lang_meta = get_language_by_name(lang_name)
    lang_code = lang_meta.code if lang_meta else "en"

    day = dt.day
    year = dt.year
    month_idx = dt.month - 1  # 0-indexed month

    months = LOCALIZED_MONTHS.get(lang_code, LOCALIZED_MONTHS["en"])
    month_name = months[month_idx]

    # Handle standard layout: {day} {month} {year}
    return f"{day} {month_name} {year}"


def format_number(val: float, lang_name: str = None, dec_places: int = 2) -> str:
    """
    Format a number with correct decimal and thousands separator.
    """
    if lang_name is None:
        lang_name = st.session_state.get("language", "English")

    # Indian numbering formats use standard dot decimal separator, comma thousands separator
    # This aligns nicely with standard system behaviors.
    return f"{val:,.{dec_places}f}"


def format_currency(val: float, lang_name: str = None) -> str:
    """
    Format currency using the Indian numbering system convention.
    Example: 150000 -> ₹1,50,000
    """
    s = f"{int(val)}"
    if len(s) <= 3:
        return f"₹{s}"

    last_three = s[-3:]
    remaining = s[:-3]
    parts = []
    while remaining:
        parts.append(remaining[-2:])
        remaining = remaining[:-2]
    parts.reverse()
    formatted = ",".join(parts) + "," + last_three
    return f"₹{formatted}"


def get_direction_styles(lang_name: str = None) -> dict[str, str]:
    """
    Returns text direction styles (direction and alignment) for RTL support.
    Indian languages are LTR, but we add future-proof support here.
    """
    if lang_name is None:
        lang_name = st.session_state.get("language", "English")

    lang_meta = get_language_by_name(lang_name)
    is_rtl = lang_meta.is_rtl if lang_meta else False

    if is_rtl:
        return {"direction": "rtl", "align": "right", "css_class": "rtl-container"}
    return {"direction": "ltr", "align": "left", "css_class": "ltr-container"}


def translate_dynamic_content_with_gemini(content: str, lang_name: str = None) -> str:
    """
    Uses Gemini API to dynamically translate content (disease descriptions, chatbot replies, reports, etc.)
    with a structured translation instruction prompt.
    Falls back to public Google Translate adapter if API keys are missing or requests fail.
    """
    if not content.strip():
        return content

    if lang_name is None:
        lang_name = st.session_state.get("language", "English")

    if lang_name == "English":
        return content

    # Check for api keys
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            prompt = f"""You are a professional translator.

Translate the content into {lang_name}.

Rules:
* Preserve formatting
* Preserve meaning
* Preserve markdown
* Preserve tables
* Preserve bullet points
* Do not summarize
* Do not add explanations

Content to translate:
{content}"""
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }

            resp = httpx.post(url, headers=headers, json=payload, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                translated = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if translated:
                    logger.info(f"Gemini translated dynamic content successfully to {lang_name}.")
                    return translated
            else:
                logger.warning(f"Gemini API returned status code {resp.status_code}. Falling back to Google Translate.")
        except Exception as e:
            logger.error(f"Gemini dynamic translation failed: {e}. Falling back to Google Translate.")

    # Fallback to Google Translate
    # Using translation_engine's Google Translate Adapter under the hood
    from translation.providers.google_adapter import GoogleTranslateAdapter
    try:
        adapter = GoogleTranslateAdapter()
        # Segment large content into paragraph chunks to avoid single request limits
        paragraphs = content.split("\n\n")
        translated_paragraphs = []
        for para in paragraphs:
            if para.strip():
                # GoogleTranslateAdapter expects display name language like "Hindi", "Telugu", etc.
                translated_para = adapter.translate_to_language(para.strip(), lang_name)
                translated_paragraphs.append(translated_para)
            else:
                translated_paragraphs.append("")
        return "\n\n".join(translated_paragraphs)
    except Exception as e:
        logger.error(f"Google Translate fallback failed: {e}")
        return content
