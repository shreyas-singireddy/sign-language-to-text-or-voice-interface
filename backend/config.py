import os

# --- General Application Settings ---
DEBUG = True

# --- Internationalization (i18n) Settings ---
SUPPORTED_LANGUAGES = ["en", "es", "hi", "te", "fr", "zh"]
BABEL_DEFAULT_LOCALE = "en"

# --- AI Inference Settings ---
# Default to local inference if no specific preference is set
DEFAULT_INFERENCE_MODE = os.getenv("DEFAULT_INFERENCE_MODE", "local").lower()  # 'local' or 'cloud'

# --- Cloud AI Service API Keys (BYOK - Bring Your Own Tokens) ---
# Users can provide their own API keys via environment variables or a UI.
# These are examples; replace with actual service names you plan to use.

# Google Cloud Translation API Key
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", None)

# Google Cloud Text-to-Speech API Key
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY", None)

# OpenAI API Key (for LLM-based translation or advanced features)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

# Add other cloud service API keys as needed

# --- Local AI Model Paths ---
# Paths to your local models for sign recognition, translation, and TTS.
# These should be relative to the backend directory or absolute paths.
LOCAL_SIGN_RECOGNITION_MODEL_PATH = os.getenv("LOCAL_SIGN_RECOGNITION_MODEL_PATH", "models/sign_recognition_model.onnx")
LOCAL_TRANSLATION_MODEL_PATH = os.getenv(
    "LOCAL_TRANSLATION_MODEL_PATH", "models/nmt_model_en_te.pt"
)  # Example: PyTorch model
LOCAL_TTS_MODEL_PATH = os.getenv("LOCAL_TTS_MODEL_PATH", "models/tts_model.pth")  # Example: Coqui TTS model

# Ollama settings (if you integrate it for LLM tasks)
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434/api")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")  # Example model name
