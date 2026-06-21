import logging

# Configuration
from backend.config import (
    DEFAULT_INFERENCE_MODE,
    GOOGLE_TRANSLATE_API_KEY,
    GOOGLE_TTS_API_KEY,
    OLLAMA_MODEL_NAME,
)

# Local AI Models
from backend.models.sign_recognizer import SignRecognizer
from backend.models.translator import LocalTranslator
from backend.models.tts_engine import LocalTTSEngine

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.sign_recognizer = SignRecognizer()
        self.local_translator = LocalTranslator()
        self.local_tts_engine = LocalTTSEngine()

        # Initialize cloud clients if API keys are available
        self.google_translate_client = None
        if GOOGLE_TRANSLATE_API_KEY:
            try:
                from google.cloud import translate_v2 as translate

                self.google_translate_client = translate.Client(api_key=GOOGLE_TRANSLATE_API_KEY)
                logger.info("Google Cloud Translation client initialized.")
            except ImportError:
                logger.warning("Google Cloud Translation library not installed. Cloud translation disabled.")
            except Exception as e:
                logger.error(f"Error initializing Google Cloud Translation client: {e}")

        self.google_tts_client = None
        if GOOGLE_TTS_API_KEY:
            try:
                from gtts import gTTS

                self.google_tts_client = gTTS  # gTTS is a simple wrapper, not a full client object
                logger.info("gTTS (Google Cloud TTS) client initialized.")
            except ImportError:
                logger.warning("gTTS library not installed. Cloud TTS disabled.")
            except Exception as e:
                logger.error(f"Error initializing gTTS client: {e}")

        # Ollama integration (placeholder for more advanced LLM tasks)
        self.ollama_client = None
        # You would typically use a library like `ollama` or `requests` to interact
        # with a local Ollama instance.
        # if DEFAULT_INFERENCE_MODE == 'local' and OLLAMA_API_BASE_URL:
        #     try:
        #         import ollama
        #         self.ollama_client = ollama.Client(host=OLLAMA_API_BASE_URL)
        #         logger.info(f"Ollama client initialized for model: {OLLAMA_MODEL_NAME}")
        #     except ImportError:
        #         logger.warning("Ollama Python client not installed. Local LLM features disabled.")
        #     except Exception as e:
        #         logger.error(f"Error initializing Ollama client: {e}")

    def process_sign_language(
        self, video_frame_data, target_lang: str, inference_mode: str | None = None
    ) -> tuple[str, str | None]:
        """
        Processes sign language input, translates it, and generates voice output.
        Returns the translated text and the path to the audio file.
        """
        if inference_mode is None:
            inference_mode = DEFAULT_INFERENCE_MODE

        # 1. Sign Language Recognition (always local for now, as it's video processing)
        recognized_text = self.sign_recognizer.recognize(video_frame_data)
        logger.info(f"Recognized text: '{recognized_text}'")

        # 2. Text Translation
        translated_text = recognized_text  # Default to no translation if not performed
        if inference_mode == "cloud" and self.google_translate_client:
            try:
                # Cloud translation using BYOK
                result = self.google_translate_client.translate(recognized_text, target_language=target_lang)
                translated_text = result["translatedText"]
                logger.info(f"Cloud translated text: '{translated_text}'")
            except Exception as e:
                logger.error(f"Google Cloud Translation failed: {e}. Falling back to local translation.")
                translated_text = self.local_translator.translate(
                    recognized_text, "en", target_lang
                )  # Assuming 'en' as source
        else:
            translated_text = self.local_translator.translate(
                recognized_text, "en", target_lang
            )  # Assuming 'en' as source

        # 3. Text-to-Speech (TTS)
        audio_file_path = f"output_audio_{target_lang}.mp3"  # Or a more dynamic naming/storage
        if inference_mode == "cloud" and self.google_tts_client:
            try:
                # Cloud TTS using BYOK (gTTS)
                tts = self.google_tts_client(text=translated_text, lang=target_lang)
                tts.save(audio_file_path)
                logger.info(f"Cloud TTS generated audio: {audio_file_path}")
            except Exception as e:
                logger.error(f"Google Cloud TTS (gTTS) failed: {e}. Falling back to local TTS.")
                audio_file_path = self.local_tts_engine.generate_audio(translated_text, target_lang, audio_file_path)
        else:
            audio_file_path = self.local_tts_engine.generate_audio(translated_text, target_lang, audio_file_path)

        return translated_text, audio_file_path

    # Example of how Ollama could be used for more advanced text processing
    def query_ollama(self, prompt: str, model: str = OLLAMA_MODEL_NAME) -> str:
        if self.ollama_client:
            try:
                # response = self.ollama_client.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
                # return response['message']['content']
                return f"Ollama response for '{prompt}' using {model}"  # Mock response
            except Exception as e:
                logger.error(f"Ollama query failed: {e}")
                return "Error: Ollama service unavailable or misconfigured."
        else:
            return "Ollama client not initialized. Local LLM features are disabled."
