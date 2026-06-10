"""
SignBridge AI — Layer 5: Translation Engine Core
Orchestrates the full sign-to-text translation pipeline:
  1. Token normalization (grammar_fixer)
  2. Grammar analysis
  3. Signs → English (provider)
  4. Grammar correction (grammar_fixer)
  5. Language translation (provider)
  6. Context storage (context_manager)

This engine is the sole public API for Layer 5.
All other layers call translation_engine.translate().
"""
import time
from datetime import datetime, timezone
from typing import List, Optional

from translation.schemas import (
    TranslationRequest,
    TranslationResult,
    TranslationProvider,
    GrammarAnalysis,
)
from translation.grammar_fixer import grammar_fixer
from translation.context_manager import context_manager
from translation.providers.rule_based import RuleBasedProvider
from translation.providers.google_adapter import GoogleTranslateAdapter
from config.logger import setup_logger

logger = setup_logger("translation.engine")


class TranslationEngine:
    """
    Layer 5 Translation Engine.
    Converts recognized sign sequences from Layer 4 into natural language text.

    Architecture:
        Layer 4 GesturePrediction
            → TranslationEngine.translate(request)
                → GrammarFixer.normalize_token_sequence()
                → GrammarAnalysis build
                → Provider.signs_to_english()
                → GrammarFixer.fix()
                → Provider.translate_to_language()
                → ContextManager.add_turn()
            → TranslationResult
    """

    def __init__(self):
        self._providers = {
            TranslationProvider.RULE_BASED: RuleBasedProvider(),
            TranslationProvider.GOOGLE: GoogleTranslateAdapter(),
        }
        self._default_provider = TranslationProvider.RULE_BASED
        logger.info("TranslationEngine initialized with providers: rule_based, google")

    def translate(self, request: TranslationRequest) -> TranslationResult:
        """
        Execute the full translation pipeline for a sign sequence.

        Args:
            request: TranslationRequest with recognized_signs, target_language, provider, etc.

        Returns:
            TranslationResult with final_translation and full diagnostic information
        """
        start_time = time.perf_counter()

        # ── Step 1: Normalize tokens ──────────────────────────────────────────
        normalized_tokens = grammar_fixer.normalize_token_sequence(request.recognized_signs)
        if not normalized_tokens:
            logger.warning("Empty token sequence after normalization.")
            return self._empty_result(request)

        # ── Step 2: Grammar analysis ─────────────────────────────────────────
        grammar = self._analyze_grammar(request.recognized_signs, normalized_tokens)

        # ── Step 3: Resolve provider ─────────────────────────────────────────
        provider_key = request.provider
        provider = self._providers.get(provider_key, self._providers[self._default_provider])

        # ── Step 4: Retrieve context ─────────────────────────────────────────
        session_id = context_manager.get_or_create_session(None)
        context_strings = context_manager.get_context_strings(session_id)
        context_applied = len(context_strings) > 0

        # ── Step 5: Signs → English ───────────────────────────────────────────
        english_raw = provider.signs_to_english(normalized_tokens, context_strings)

        # ── Step 6: Grammar correction ────────────────────────────────────────
        english_corrected = grammar_fixer.fix(english_raw, target_language="English")

        # ── Step 7: Translate to target language ──────────────────────────────
        if request.target_language == "English":
            final_translation = english_corrected
        else:
            final_translation = provider.translate_to_language(english_corrected, request.target_language)
            final_translation = grammar_fixer.fix(final_translation, target_language=request.target_language)

        # ── Step 8: Generate alternatives ────────────────────────────────────
        alternatives = self._generate_alternatives(normalized_tokens, english_corrected, request.target_language)

        # ── Step 9: Store in context window ──────────────────────────────────
        context_manager.add_turn(
            session_id=session_id,
            signs=normalized_tokens,
            translation=english_corrected,
            language=request.target_language
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            f"Translation complete in {elapsed_ms}ms: "
            f"{normalized_tokens} → '{final_translation}' ({request.target_language})"
        )

        return TranslationResult(
            original_signs=request.recognized_signs,
            english_base=english_corrected,
            final_translation=final_translation,
            target_language=request.target_language,
            provider_used=provider_key,
            confidence=request.confidence,
            grammar_analysis=grammar,
            context_applied=context_applied,
            alternatives=alternatives,
            metadata={
                "elapsed_ms": elapsed_ms,
                "normalized_tokens": normalized_tokens,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def translate_simple(
        self,
        signs: List[str],
        target_language: str = "English",
        confidence: float = 1.0
    ) -> str:
        """
        Simplified translation interface returning just the final text string.
        Ideal for direct calls from Streamlit pages or the speech engine.

        Args:
            signs: List of recognized sign tokens
            target_language: Target output language
            confidence: Layer 4 confidence score

        Returns:
            Final translated string
        """
        request = TranslationRequest(
            recognized_signs=signs,
            target_language=target_language,
            confidence=confidence,
        )
        result = self.translate(request)
        return result.final_translation

    def _analyze_grammar(self, raw_tokens: List[str], normalized: List[str]) -> GrammarAnalysis:
        """Build a GrammarAnalysis object for diagnostic reporting."""
        subject_detected = any(t in {"I", "YOU", "HE", "SHE", "WE", "THEY"} for t in normalized)

        # Tense inference from temporal keywords
        future_markers = {"WILL", "GOING", "TOMORROW", "LATER", "SOON"}
        past_markers = {"WAS", "DID", "HAD", "YESTERDAY", "AGO"}
        token_set = set(normalized)

        if token_set & future_markers:
            tense = "future"
        elif token_set & past_markers:
            tense = "past"
        else:
            tense = "present"

        # Sentence type inference
        question_markers = {"WHAT", "WHERE", "WHO", "WHEN", "WHY", "HOW", "CAN", "DO", "IS", "ARE"}
        exclamation_markers = {"EMERGENCY", "SOS", "DANGER", "HELP", "FIRE"}
        imperative_markers = {"PLEASE", "CALL", "GIVE", "BRING", "TAKE", "GO", "STOP", "COME"}

        if token_set & exclamation_markers:
            sentence_type = "exclamatory"
        elif token_set & question_markers and "?" in str(normalized):
            sentence_type = "interrogative"
        elif token_set & imperative_markers and not subject_detected:
            sentence_type = "imperative"
        else:
            sentence_type = "declarative"

        # Complexity: ratio of unique tokens to total tokens
        complexity = round(len(set(normalized)) / max(len(normalized), 1), 2)

        return GrammarAnalysis(
            raw_tokens=raw_tokens,
            normalized_tokens=normalized,
            subject_detected=subject_detected,
            tense_inferred=tense,
            sentence_type=sentence_type,
            complexity_score=min(complexity, 1.0),
        )

    def _generate_alternatives(
        self,
        tokens: List[str],
        english_base: str,
        target_language: str
    ) -> List[str]:
        """
        Generate 1-2 alternative phrasings for the translation.
        Used in the UI to offer the user phrasing choices.
        """
        alternatives = []
        rule_provider = self._providers[TranslationProvider.RULE_BASED]

        # Try reversing token order for an alternative reading
        if len(tokens) > 1:
            reversed_tokens = list(reversed(tokens))
            alt_english = rule_provider.signs_to_english(reversed_tokens)
            alt_english = grammar_fixer.fix(alt_english)
            if alt_english != english_base:
                if target_language == "English":
                    alternatives.append(alt_english)
                else:
                    alt_translated = rule_provider.translate_to_language(alt_english, target_language)
                    if alt_translated != english_base:
                        alternatives.append(alt_translated)

        return alternatives[:2]  # Max 2 alternatives

    def _empty_result(self, request: TranslationRequest) -> TranslationResult:
        """Return an empty/null result for degenerate inputs."""
        return TranslationResult(
            original_signs=request.recognized_signs,
            english_base="",
            final_translation="",
            target_language=request.target_language,
            provider_used=request.provider,
            confidence=0.0,
            grammar_analysis=GrammarAnalysis(
                raw_tokens=request.recognized_signs,
                normalized_tokens=[],
                subject_detected=False,
                tense_inferred="present",
                sentence_type="declarative",
                complexity_score=0.0,
            ),
            context_applied=False,
            alternatives=[],
            metadata={"error": "empty_token_sequence"}
        )

    def set_default_provider(self, provider: TranslationProvider) -> None:
        """Change the default provider at runtime."""
        self._default_provider = provider
        logger.info(f"Default translation provider set to: {provider.value}")

    def get_provider_status(self) -> dict:
        """Return health status of all registered providers."""
        return {
            name.value: provider.health_check()
            for name, provider in self._providers.items()
        }


# Global singleton instance — all layers import this
translation_engine = TranslationEngine()
