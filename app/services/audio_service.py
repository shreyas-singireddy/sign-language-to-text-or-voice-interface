import os
from pathlib import Path
from speech.tts_engine import TTSEngine, tts_engine
from speech.schemas import TTSRequest, TTSProvider
from speech.whisper_engine import WhisperEngine
from config.logger import setup_logger

logger = setup_logger("services.audio")


class AudioService:
    def __init__(self):
        # Reuse the global singleton to avoid duplicate provider initialization
        self.tts = tts_engine
        self.whisper = WhisperEngine()

    def generate_speech(self, text: str, lang_code: str = "en-US") -> bytes:
        """
        Synthesizes text into speech using gTTS (internet-dependent) with
        a mock WAV fallback when offline.

        Returns audio bytes (MP3 from gTTS, WAV from fallback).

        BUG-001 FIX: Previously passed TTSRequest missing required provider
        field, causing intermittent failures. Now constructs TTSRequest fully
        and extracts audio_bytes safely.
        """
        logger.info(f"Synthesizing text: '{text}' using language code: {lang_code}")
        try:
            request = TTSRequest(
                text=text,
                lang_code=lang_code,
                provider=TTSProvider.GTTS,
                slow=False,
                tld="com",
            )
            result = self.tts.synthesize(request)
            if result and result.audio_bytes:
                return result.audio_bytes
            logger.warning("TTS synthesis returned empty bytes.")
            return b""
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return b""

    def speech_to_text(self, audio_filepath: str) -> str:
        """
        Transcribes audio file to text.
        """
        logger.info(f"Transcribing audio file: {audio_filepath}")
        if not os.path.exists(audio_filepath):
            logger.error("Audio file does not exist.")
            return ""
        try:
            return self.whisper.transcribe(audio_filepath)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def get_voice_options(self) -> list:
        """
        Returns list of available TTS voices.
        """
        return self.tts.get_all_voices()


audio_service = AudioService()
