import pytest
from datetime import datetime
from multilingual.locale_formatter import locale_formatter

def test_format_number():
    # Test fallback
    val = 1234.567
    res = locale_formatter.format_number(val, "NonExistentLanguage", 2)
    assert res == "1234.57"

    # Test with standard language (English)
    res_en = locale_formatter.format_number(val, "English", 2)
    assert "1,234.57" in res_en or "1234.57" in res_en

    # Test negative number
    res_neg = locale_formatter.format_number(-50.5, "English", 1)
    assert "-50.5" in res_neg

def test_format_confidence():
    res = locale_formatter.format_confidence(0.9256, "English")
    assert "92.6%" in res or "92.6" in res

def test_format_date():
    dt = datetime(2026, 6, 11, 12, 0, 0)
    res = locale_formatter.format_date(dt, "NonExistent")
    assert res == "2026-06-11"

    res_en = locale_formatter.format_date(dt, "English")
    assert len(res_en) > 0

def test_format_duration():
    res1 = locale_formatter.format_duration(125, "English")
    assert res1 == "2m 5s"

    res2 = locale_formatter.format_duration(45, "English")
    assert res2 == "45s"

def test_get_ui_strings():
    res_en = locale_formatter.get_ui_strings("English")
    assert res_en["start"] == "Start"

    res_hi = locale_formatter.get_ui_strings("Hindi")
    assert res_hi["start"] == "शुरू करें"

    res_unknown = locale_formatter.get_ui_strings("UnknownLanguage")
    assert res_unknown["start"] == "Start"
