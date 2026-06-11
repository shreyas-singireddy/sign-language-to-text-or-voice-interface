import os
from pathlib import Path

from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from root .env if it exists, otherwise check backend/.env
root_env = BASE_DIR / ".env"
backend_env = BASE_DIR / "backend" / ".env"

if root_env.exists():
    load_dotenv(dotenv_path=root_env)
elif backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
else:
    load_dotenv()

# App Configuration
PROJECT_NAME = os.getenv("PROJECT_NAME", "SignBridge AI")
DB_NAME = os.getenv("DB_NAME", "signbridge_ai")
MONGO_URI = os.getenv("MONGO_URI", "")

# AI Engine Configuration
WEBCAM_SOURCE = int(os.getenv("WEBCAM_SOURCE", "0"))
MP_STATIC_IMAGE_MODE = os.getenv("MP_STATIC_IMAGE_MODE", "False").lower() in (
    "true",
    "1",
    "t",
)
MP_MAX_NUM_HANDS = int(os.getenv("MP_MAX_NUM_HANDS", "2"))
MP_MIN_DETECTION_CONFIDENCE = float(os.getenv("MP_MIN_DETECTION_CONFIDENCE", "0.5"))
MP_MIN_TRACKING_CONFIDENCE = float(os.getenv("MP_MIN_TRACKING_CONFIDENCE", "0.5"))

# Model Thresholds
GESTURE_CONFIDENCE_THRESHOLD = float(os.getenv("GESTURE_CONFIDENCE_THRESHOLD", "0.7"))
SEQUENCE_BUFFER_SIZE = int(
    os.getenv("SEQUENCE_BUFFER_SIZE", "30")
)  # Number of frames to check for sequence models

# Paths
MODELS_DIR = BASE_DIR / "assets" / "models"
DATASETS_DIR = BASE_DIR / "ai_engine" / "datasets" / "data"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# List of Supported Gestures
SUPPORTED_GESTURES = [
    "HELLO",
    "THANKS",
    "YES",
    "NO",
    "PLEASE",
    "SORRY",
    "HELP",
    "GOOD MORNING",
    "GOOD NIGHT",
]

# Supported Speech Languages
SUPPORTED_LANGUAGES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Chinese": "zh-CN",
    "Japanese": "ja-JP",
    "Arabic": "ar-SA",
    "Portuguese": "pt-PT",
    "Russian": "ru-RU",
    "Italian": "it-IT",
    "Korean": "ko-KR",
    "Bengali": "bn-IN",
    "Tamil": "ta-IN",
    "Urdu": "ur-PK",
}
