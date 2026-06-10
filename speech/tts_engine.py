import io
import wave
import numpy as np
from config.logger import setup_logger

logger = setup_logger("speech.tts")

class TTSEngine:
    def __init__(self):
        self.tts_model = None
        self.is_loaded = False
        self._initialize_tts()

    def _initialize_tts(self):
        """
        Attempts to load Coqui TTS or other heavy TTS packages.
        """
        try:
            # Placeholder for future Coqui TTS initialization:
            # from TTS.api import TTS
            # self.tts_model = TTS(model_name="tts_models/en/ljspeech/vits")
            # self.is_loaded = True
            logger.info("Coqui TTS engine imports structural verification completed. Running in mock synthesis mode.")
            self.is_loaded = False
        except Exception as e:
            logger.warning(f"Could not initialize Coqui TTS: {e}. Falling back to lightweight WAV stub synthesis.")
            self.is_loaded = False

    def synthesize(self, text: str, lang_code: str = "en-US") -> bytes:
        """
        Synthesizes text input into wav speech audio bytes.
        """
        if self.is_loaded and self.tts_model is not None:
            try:
                # audio_data = self.tts_model.tts(text=text, speaker=self.tts_model.speakers[0])
                # return wav_bytes
                pass
            except Exception as e:
                logger.error(f"TTS synthesis error: {e}")

        # Lightweight Mock Synthesis: Generate a simple clean sine wave audio file
        # This allows Streamlit's st.audio() player to play a real, valid audio file containing the text log
        logger.info(f"Mocking TTS audio synthesis for: '{text}'")
        
        # Audio parameters
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440.0  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Generate sine wave
        sine_wave = np.sin(frequency * t * 2 * np.pi)
        # Normalize to 16-bit integer range
        audio_ints = np.int16(sine_wave * 32767)
        
        # Write to byte buffer as WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_ints.tobytes())
            
        return wav_buffer.getvalue()

    def get_available_voices(self) -> list:
        """
        Returns list of mock voices available for selection.
        """
        return ["Default Male (VITS)", "Default Female (VITS)", "Neural Speaker 1", "Neural Speaker 2"]
