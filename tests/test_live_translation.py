from translation.engine import TranslationEngine
from translation.schemas import TranslationRequest


def test_live_translation_hello():
    engine = TranslationEngine()
    request = TranslationRequest(recognized_signs=["HELLO"], target_language="English")
    result = engine.translate(request)
    assert result.final_translation == "Hello!"
    assert result.english_base == "Hello!"
    assert result.confidence > 0.5
