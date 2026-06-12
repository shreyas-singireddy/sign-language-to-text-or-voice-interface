"""
SignBridge AI — Layer 6: Speech Provider Base
Abstract base class defining the contract for all TTS provider adapters.
"""

from abc import ABC, abstractmethod

from speech.schemas import AvailableVoice, TTSResult


class BaseTTSProvider(ABC):
    """
    Abstract base class for text-to-speech provider adapters.
    All providers implement synthesize() returning raw audio bytes.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider."""

    @property
    @abstractmethod
    def audio_format(self) -> str:
        """Audio format output: 'mp3' or 'wav'."""

    @abstractmethod
    def synthesize(self, text: str, lang_code: str = "en", slow: bool = False, tld: str = "com") -> TTSResult:
        """
        Synthesize text into audio bytes.

        Args:
            text: Text to speak
            lang_code: BCP-47 language code
            slow: Whether to use slow speech rate
            tld: Domain TLD for accent variation

        Returns:
            TTSResult with audio_bytes and metadata
        """

    @abstractmethod
    def get_available_voices(self) -> list[AvailableVoice]:
        """Return all voices available from this provider."""

    def health_check(self) -> bool:
        """
        Check if the provider is operational.
        Override in subclasses requiring network or resource validation.
        """
        return True
