from translation.schemas import TranslationRequest


def test_api_translation_request_schema():
    req = TranslationRequest(recognized_signs=["HELLO", "YES"], target_language="Spanish")
    assert req.recognized_signs == ["HELLO", "YES"]
    assert req.target_language == "Spanish"
