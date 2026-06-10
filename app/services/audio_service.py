import os
from pathlib import Path
from speech.tts_engine import TTSEngine
from speech.whisper_engine import WhisperEngine
from config.logger import setup_logger

logger = setup_logger("services.audio")

class AudioService:
    def __init__(self):
        self.tts = TTSEngine()
        self.whisper = WhisperEngine()

    def generate_speech(self, text: str, lang_code: str = "en-US") -> bytes:
        """
        Synthesizes text into speech. Returns audio bytes.
        """
        logger.info(f"Synthesizing text: '{text}' using language code: {lang_code}")
        return self.tts.synthesize(text, lang_code)

    def speech_to_text(self, audio_filepath: str) -> str:
        """
        Transcribes audio file to text.
        """
        logger.info(f"Transcribing audio file: {audio_filepath}")
        if not os.path.exists(audio_filepath):
            logger.error("Audio file does not exist.")
            return ""
        return self.whisper.transcribe(audio_filepath)

    def get_voice_options(self) -> list:
        """
        Returns list of available TTS voices.
        """
        return self.tts.get_available_voices()

audio_service = AudioService()
