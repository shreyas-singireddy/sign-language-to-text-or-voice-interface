"""
SignBridge AI — Layer 5: Grammar Fixer
Post-processes raw English output from providers to apply additional
grammar correction rules: punctuation, capitalization, contraction
normalization, and sentence completeness checks.
"""

import re

from config.logger import setup_logger

logger = setup_logger("translation.grammar_fixer")

# Pairs of (regex pattern, replacement) applied in order
GRAMMAR_RULES: list[tuple] = [
    # Fix double spaces
    (r" {2,}", " "),
    # Capitalize first character of sentence
    (r"^([a-z])", lambda m: m.group(1).upper()),
    # Ensure sentence ends with punctuation
    (r"([^.!?])$", r"\1."),
    # Fix "i " → "I " (standalone pronoun)
    (r"\bi\b", "I"),
    # Fix spaced contractions (do n't → don't)
    (
        r"\b(do|does|did|is|are|was|were|have|has|had|will|would|should|could|can|might|must|shall) n'?t\b",
        lambda m: m.group(0).replace(" n't", "n't").replace(" nt", "n't"),
    ),
    # Remove leading/trailing whitespace
    (r"^\s+|\s+$", ""),
    # Fix multiple punctuation (e.g. "!!!" → "!")
    (r"([.!?]){2,}", r"\1"),
    # Fix comma before period
    (r",\.", "."),
    # Normalize "i'm" → "I'm"
    (r"\bi'm\b", "I'm"),
    (r"\bi've\b", "I've"),
    (r"\bi'll\b", "I'll"),
    (r"\bi'd\b", "I'd"),
]

# Known filler tokens that should be silently removed from the sentence
FILLER_TOKENS = {"UM", "UH", "AH", "ERR", "HMHM", "MMM", "HMM", "EH"}

# Words that should always be title-case
PROPER_NOUNS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "english",
    "hindi",
    "spanish",
    "french",
    "german",
    "signbridge",
}


class GrammarFixer:
    """
    Post-processing grammar correction engine for translated text.
    Applies a chain of regex and rule-based transformations to produce
    clean, publication-quality natural language output.
    """

    def fix(self, text: str, target_language: str = "English") -> str:
        """
        Apply all grammar fixes to the provided text.

        Args:
            text: Raw translated text to fix
            target_language: Language of the text (non-English text skips most rules)

        Returns:
            Grammar-corrected text
        """
        if not text or not text.strip():
            return text

        # Only apply English-specific grammar rules for English
        if target_language == "English":
            text = self._apply_english_rules(text)
        else:
            # For non-English languages: only apply punctuation and spacing rules
            text = self._apply_universal_rules(text)

        return text.strip()

    def _apply_english_rules(self, text: str) -> str:
        """Apply full English grammar rule chain."""
        for pattern, replacement in GRAMMAR_RULES:
            if callable(replacement):
                text = re.sub(pattern, replacement, text)
            else:
                text = re.sub(
                    pattern,
                    replacement,
                    text,
                    flags=re.IGNORECASE if r"\b" in pattern else 0,
                )

        # Title-case proper nouns
        words = text.split()
        corrected_words = []
        for word in words:
            clean = word.lower().strip(".!?,;:")
            if clean in PROPER_NOUNS:
                corrected_words.append(word[0].upper() + word[1:] if word else word)
            else:
                corrected_words.append(word)
        text = " ".join(corrected_words)

        # Final: capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    def _apply_universal_rules(self, text: str) -> str:
        """Apply minimal universal rules (spacing, punctuation) for non-English text."""
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"^\s+|\s+$", "", text)
        if text and text[-1] not in ".!?。！？":
            text += "."
        return text

    def remove_filler_tokens(self, tokens: list[str]) -> list[str]:
        """
        Remove filler/noise tokens from a sign sequence before translation.

        Args:
            tokens: Raw sign token list

        Returns:
            Cleaned token list with filler tokens removed
        """
        return [t for t in tokens if t.upper() not in FILLER_TOKENS]

    def normalize_token_sequence(self, tokens: list[str]) -> list[str]:
        """
        Normalize a token sequence: uppercase, strip, deduplicate consecutives,
        remove fillers.

        Args:
            tokens: Raw tokens from Layer 4

        Returns:
            Fully normalized token list
        """
        # Uppercase and strip
        normalized = [t.strip().upper() for t in tokens if t.strip()]
        # Remove fillers
        normalized = self.remove_filler_tokens(normalized)
        # Deduplicate consecutive
        deduped = []
        for token in normalized:
            if not deduped or deduped[-1] != token:
                deduped.append(token)
        return deduped


grammar_fixer = GrammarFixer()
