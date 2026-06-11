"""
SignBridge AI — Layer 6: Speech Engine Schemas
Pydantic I/O contracts for all TTS and STT operations.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TTSProvider(str, Enum):
    """Available TTS providers."""

    GTTS = "gtts"
    BROWSER = "browser"
    MOCK = "mock"


class STTProvider(str, Enum):
    """Available STT providers."""

    BROWSER = "browser"
    MOCK = "mock"


class VoiceProfile(BaseModel):
    """Configuration profile for a TTS voice synthesis request."""

    name: str = Field(description="Human-readable voice profile name")
    lang_code: str = Field(description="BCP-47 language code (e.g. 'en-US')")
    slow: bool = Field(default=False, description="Slow speech rate for accessibility")
    tld: str = Field(default="com", description="Google TTS TLD for accent variant")


class TTSRequest(BaseModel):
    """Input request for text-to-speech synthesis."""

    text: str = Field(..., description="Text to synthesize into audio", min_length=1)
    lang_code: str = Field(default="en", description="BCP-47 language code")
    provider: TTSProvider = Field(
        default=TTSProvider.GTTS, description="TTS provider to use"
    )
    slow: bool = Field(default=False, description="Synthesize at reduced speed")
    tld: str = Field(default="com", description="TLD for accent variation")


class TTSResult(BaseModel):
    """Output result from TTS synthesis."""

    audio_bytes: bytes = Field(description="Raw WAV or MP3 audio bytes")
    format: str = Field(default="mp3", description="Audio format: mp3 or wav")
    provider_used: TTSProvider = Field(description="Provider that generated the audio")
    text_synthesized: str = Field(description="Exact text that was synthesized")
    lang_code: str = Field(description="Language code used for synthesis")
    duration_estimate_seconds: float | None = Field(
        default=None, description="Estimated audio duration in seconds"
    )
    success: bool = Field(default=True)
    error: str | None = Field(default=None)


class STTResult(BaseModel):
    """Output result from speech-to-text recognition."""

    transcript: str = Field(description="Recognized speech text")
    confidence: float = Field(ge=0.0, le=1.0, description="Recognition confidence")
    provider_used: STTProvider = Field(description="Provider used for recognition")
    language: str = Field(description="Language of the transcript")
    is_final: bool = Field(default=True, description="Whether this is a final result")


class AvailableVoice(BaseModel):
    """Describes a single available TTS voice."""

    id: str = Field(description="Unique voice identifier")
    name: str = Field(description="Human-readable voice name")
    language: str = Field(description="Language name (e.g. 'English')")
    lang_code: str = Field(description="BCP-47 code")
    provider: TTSProvider = Field(description="Which provider delivers this voice")
    accent: str | None = Field(default=None, description="Accent variant if applicable")
