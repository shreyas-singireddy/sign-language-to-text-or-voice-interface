import datetime

import streamlit as st

from src.config.languages import SUPPORTED_LANGUAGES, get_language_by_code, get_language_by_name
from src.services.translation_service import format_currency, format_date, format_number, get_direction_styles, t


def test_language_registry():
    # Registry integrity
    assert "English" in SUPPORTED_LANGUAGES
    assert "Hindi" in SUPPORTED_LANGUAGES
    assert "Portuguese" in SUPPORTED_LANGUAGES

    # Retrieval functions
    meta_en = get_language_by_code("en")
    assert meta_en is not None
    assert meta_en.name == "English"

    meta_hi = get_language_by_name("Hindi")
    assert meta_hi is not None
    assert meta_hi.code == "hi"

    assert get_language_by_code("non_existent") is None
    assert get_language_by_name("non_existent") is None


def test_translation_helper():
    # Setup active language in session state
    st.session_state["language"] = "English"

    # Test English translation lookup
    val = t("splash_title")
    assert val == "SIGNBRIDGE AI"

    # Test key fallback
    val_fallback = t("non_existent_key_xyz")
    assert val_fallback == "non_existent_key_xyz"

    # Switch language to Hindi and test fallback
    st.session_state["language"] = "Hindi"
    # test a key that exists in English but might be missing in Hindi fallback
    val_fallback_en = t("em_title")
    assert len(val_fallback_en) > 0


def test_locale_formatters():
    # Test number formatting
    num_str = format_number(12345.678, "English", 2)
    assert num_str == "12,345.68"

    # Test currency formatting (Indian standard)
    curr_str = format_currency(150000, "English")
    assert curr_str == "₹1,50,000"

    curr_str2 = format_currency(250, "English")
    assert curr_str2 == "₹250"

    # Test date formatting
    dt = datetime.date(2026, 6, 12)
    date_str_en = format_date(dt, "English")
    assert "June" in date_str_en
    assert "2026" in date_str_en

    date_str_hi = format_date(dt, "Hindi")
    assert "जून" in date_str_hi


def test_direction_styles():
    # LTR languages
    styles_en = get_direction_styles("English")
    assert styles_en["direction"] == "ltr"

    # Non-existent language fallback
    styles_fallback = get_direction_styles("NonExistent")
    assert styles_fallback["direction"] == "ltr"
