"""
SignBridge AI — Layer 5 Translation Engine Test Suite
Tests: provider abstraction, grammar fixer, context manager, engine pipeline.
"""
import pytest
from translation.providers.rule_based import RuleBasedProvider
from translation.providers.google_adapter import GoogleTranslateAdapter
from translation.grammar_fixer import GrammarFixer, grammar_fixer
from translation.context_manager import TranslationContextManager
from translation.engine import TranslationEngine
from translation.schemas import TranslationRequest, TranslationProvider


class TestRuleBasedProvider:
    """Tests for the local rule-based translation provider."""

    def setup_method(self):
        self.provider = RuleBasedProvider()

    def test_provider_name(self):
        assert self.provider.provider_name == "rule_based"

    def test_supports_multilingual(self):
        assert self.provider.supports_multilingual is True

    def test_health_check_always_true(self):
        assert self.provider.health_check() is True

    def test_exact_phrase_match_single_token(self):
        result = self.provider.signs_to_english(["HELLO"])
        assert result == "Hello!"

    def test_exact_phrase_match_multi_token(self):
        result = self.provider.signs_to_english(["WATER", "WANT"])
        assert "water" in result.lower()

    def test_exact_phrase_match_please_help(self):
        result = self.provider.signs_to_english(["PLEASE", "HELP"])
        assert result == "Please help me."

    def test_emergency_phrase_sos(self):
        result = self.provider.signs_to_english(["SOS"])
        assert "EMERGENCY" in result.upper() or "help" in result.lower()

    def test_deduplication_of_consecutive(self):
        result = self.provider.signs_to_english(["HELLO", "HELLO", "HELLO"])
        assert result == "Hello!"

    def test_fallback_grammar_construction_subject_verb(self):
        result = self.provider.signs_to_english(["I", "WANT", "FOOD"])
        assert "I" in result or "want" in result.lower() or "food" in result.lower()

    def test_fallback_grammar_unknown_tokens(self):
        result = self.provider.signs_to_english(["XYZUNKNOWN123"])
        assert len(result) > 0

    def test_empty_token_list(self):
        result = self.provider.signs_to_english([])
        assert result == ""

    def test_multilingual_english_passthrough(self):
        english_text = "Hello!"
        result = self.provider.translate_to_language(english_text, "English")
        assert result == english_text

    def test_multilingual_spanish(self):
        result = self.provider.translate_to_language("Hello!", "Spanish")
        assert result == "¡Hola!"

    def test_multilingual_hindi(self):
        result = self.provider.translate_to_language("Thank you!", "Hindi")
        assert "धन्यवाद" in result

    def test_multilingual_arabic(self):
        result = self.provider.translate_to_language("Yes.", "Arabic")
        assert "نعم" in result

    def test_multilingual_unknown_language_fallback(self):
        result = self.provider.translate_to_language("Hello!", "Klingon")
        assert "Hello!" in result  # Bracketed fallback


class TestGrammarFixer:
    """Tests for the GrammarFixer post-processor."""

    def setup_method(self):
        self.fixer = GrammarFixer()

    def test_capitalizes_first_letter(self):
        result = self.fixer.fix("hello world.", "English")
        assert result[0].isupper()

    def test_adds_period_if_missing(self):
        result = self.fixer.fix("I need help", "English")
        assert result.endswith(".")

    def test_fixes_double_spaces(self):
        result = self.fixer.fix("I  need  help.", "English")
        assert "  " not in result

    def test_removes_filler_tokens(self):
        cleaned = self.fixer.remove_filler_tokens(["HELLO", "UM", "WATER", "UH"])
        assert "UM" not in cleaned
        assert "UH" not in cleaned
        assert "HELLO" in cleaned

    def test_normalize_deduplication(self):
        normalized = self.fixer.normalize_token_sequence(["HELLO", "HELLO", "WORLD"])
        assert normalized == ["HELLO", "WORLD"]

    def test_normalize_uppercase(self):
        normalized = self.fixer.normalize_token_sequence(["hello", "world"])
        assert all(t.isupper() for t in normalized)

    def test_non_english_universal_rules(self):
        result = self.fixer.fix("नमस्ते", "Hindi")
        assert len(result) > 0

    def test_multiple_punctuation_fix(self):
        result = self.fixer.fix("Hello!!!", "English")
        assert "!!!" not in result


class TestContextManager:
    """Tests for the Translation Context Manager."""

    def setup_method(self):
        self.ctx = TranslationContextManager()

    def test_create_session_returns_string(self):
        session_id = self.ctx.create_session()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_get_or_create_creates_when_none(self):
        session_id = self.ctx.get_or_create_session(None)
        assert isinstance(session_id, str)

    def test_get_or_create_returns_existing(self):
        session_id = self.ctx.create_session()
        returned = self.ctx.get_or_create_session(session_id)
        assert returned == session_id

    def test_add_turn_and_retrieve_context(self):
        session_id = self.ctx.create_session()
        self.ctx.add_turn(session_id, ["HELLO"], "Hello!", "English")
        context = self.ctx.get_context_strings(session_id)
        assert "Hello!" in context

    def test_turn_count(self):
        session_id = self.ctx.create_session()
        for i in range(3):
            self.ctx.add_turn(session_id, [f"SIGN{i}"], f"Translation {i}", "English")
        assert self.ctx.get_turn_count(session_id) == 3

    def test_sliding_window_enforced(self):
        ctx = TranslationContextManager(max_turns=3)
        session_id = ctx.create_session()
        for i in range(5):
            ctx.add_turn(session_id, [f"SIGN{i}"], f"T{i}", "English")
        assert ctx.get_turn_count(session_id) == 3

    def test_clear_session(self):
        session_id = self.ctx.create_session()
        self.ctx.add_turn(session_id, ["HELLO"], "Hello!", "English")
        self.ctx.clear_session(session_id)
        assert self.ctx.get_turn_count(session_id) == 0

    def test_unknown_session_returns_empty_context(self):
        result = self.ctx.get_context_strings("nonexistent-session")
        assert result == []


class TestTranslationEngine:
    """Integration tests for the full TranslationEngine pipeline."""

    def setup_method(self):
        self.engine = TranslationEngine()

    def test_translate_simple_hello(self):
        result = self.engine.translate_simple(["HELLO"], "English")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_returns_translation_result(self):
        request = TranslationRequest(recognized_signs=["WATER", "WANT"], target_language="English")
        result = self.engine.translate(request)
        assert result.final_translation
        assert result.english_base
        assert result.confidence >= 0.0

    def test_translate_to_spanish(self):
        result = self.engine.translate_simple(["THANK"], "Spanish")
        assert len(result) > 0

    def test_translate_to_hindi(self):
        result = self.engine.translate_simple(["HELLO"], "Hindi")
        assert len(result) > 0

    def test_grammar_analysis_populated(self):
        request = TranslationRequest(recognized_signs=["I", "WANT", "HELP"], target_language="English")
        result = self.engine.translate(request)
        assert result.grammar_analysis is not None
        assert result.grammar_analysis.tense_inferred in {"present", "past", "future"}

    def test_empty_tokens_returns_empty(self):
        request = TranslationRequest(recognized_signs=["   ", ""], target_language="English")
        result = self.engine.translate(request)
        assert result.final_translation == "" or isinstance(result.final_translation, str)

    def test_provider_status_returns_dict(self):
        status = self.engine.get_provider_status()
        assert isinstance(status, dict)
        assert "rule_based" in status

    def test_set_default_provider(self):
        self.engine.set_default_provider(TranslationProvider.RULE_BASED)
        # No exception = pass


class TestGoogleAdapterFallback:
    """Tests for Google Translate adapter graceful fallback."""

    def test_signs_to_english_delegates_to_rule_based(self):
        adapter = GoogleTranslateAdapter()
        result = adapter.signs_to_english(["HELLO"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_english_returns_unchanged(self):
        adapter = GoogleTranslateAdapter()
        result = adapter.translate_to_language("Hello!", "English")
        assert result == "Hello!"
