from ai_engine.translation_engine.translator import translation_engine


def test_translation_engine_direct_match():
    # Direct dictionary match
    res = translation_engine.translate(["HELLO"], "English")
    assert res == "Hello!"

    res_please = translation_engine.translate(["HELLO", "PLEASE"], "English")
    assert res_please == "Hello, please."


def test_translation_engine_fallback():
    # Fallback to join and capitalize
    res = translation_engine.translate(["HELLO", "WORLD"], "English")
    assert res == "Hello world."


def test_translation_engine_multilingual():
    # Spanish mapping
    res_es = translation_engine.translate(["YES"], "Spanish")
    assert res_es == "Sí."

    res_es_neg = translation_engine.translate(["NO"], "Spanish")
    assert res_es_neg == "No."

    # Hindi mapping
    res_hi = translation_engine.translate(["YES"], "Hindi")
    assert res_hi == "हाँ।"

    # Telugu mapping
    res_te = translation_engine.translate(["YES"], "Telugu")
    assert res_te == "అవును."

    # Unsupported language
    res_unsupported = translation_engine.translate(["YES"], "German")
    assert "Translated to German" in res_unsupported


def test_translation_engine_empty():
    res = translation_engine.translate([], "English")
    assert res == ""
