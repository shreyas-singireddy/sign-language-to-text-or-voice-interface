"""
SignBridge AI — Layer 5: Translation Provider Base
Abstract base class defining the contract for all translation provider adapters.
"""

from abc import ABC, abstractmethod


class BaseTranslationProvider(ABC):
    """
    Abstract base class for all translation provider adapters.
    All providers must implement this interface to ensure
    plug-and-play swappability without modifying the engine.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier name of this provider."""

    @property
    @abstractmethod
    def supports_multilingual(self) -> bool:
        """Return True if this provider supports languages beyond English."""

    @abstractmethod
    def signs_to_english(self, tokens: list[str], context: list[str] | None = None) -> str:
        """
        Convert a list of sign tokens into a grammatically correct English sentence.

        Args:
            tokens: Ordered list of recognized sign tokens (e.g. ["WATER", "WANT"])
            context: Optional list of previous English translations for context awareness

        Returns:
            Grammatically corrected English sentence
        """

    @abstractmethod
    def translate_to_language(self, english_text: str, target_language: str) -> str:
        """
        Translate an English sentence to the target language.

        Args:
            english_text: Grammar-corrected English sentence
            target_language: Target language name (e.g. "Spanish", "Hindi")

        Returns:
            Translated text in the target language
        """

    def health_check(self) -> bool:
        """
        Verify the provider is operational.
        Override in subclasses that require network or model availability checks.

        Returns:
            True if provider is ready, False otherwise
        """
        return True
