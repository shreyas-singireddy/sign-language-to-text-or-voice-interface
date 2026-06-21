import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SignBridge AI"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # MongoDB settings
    MONGO_URI: str = Field(default="")
    DB_NAME: str = "signbridge_ai"

    # --- Internationalization (i18n) Settings ---
    SUPPORTED_LANGUAGES: list[str] = ["en", "es", "hi", "te", "fr", "zh"]
    BABEL_DEFAULT_LOCALE: str = "en"

    # --- AI Inference Settings ---
    # Default to local inference if no specific preference is set
    DEFAULT_INFERENCE_MODE: str = Field(
        default=os.getenv("DEFAULT_INFERENCE_MODE", "local").lower()
    )  # 'local' or 'cloud'

    # --- Cloud AI Service API Keys (BYOK - Bring Your Own Tokens) ---
    # Users can provide their own API keys via environment variables or a UI.
    # These are examples; replace with actual service names you plan to use.
    GOOGLE_TRANSLATE_API_KEY: str | None = Field(default=os.getenv("GOOGLE_TRANSLATE_API_KEY", None))
    GOOGLE_TTS_API_KEY: str | None = Field(default=os.getenv("GOOGLE_TTS_API_KEY", None))
    OPENAI_API_KEY: str | None = Field(default=os.getenv("OPENAI_API_KEY", None))

    # --- Local AI Model Paths ---
    # Paths to your local models for sign recognition, translation, and TTS.
    LOCAL_SIGN_RECOGNITION_MODEL_PATH: str = Field(
        default=os.getenv("LOCAL_SIGN_RECOGNITION_MODEL_PATH", "models/sign_recognition_model.onnx")
    )
    LOCAL_TRANSLATION_MODEL_PATH: str = Field(
        default=os.getenv("LOCAL_TRANSLATION_MODEL_PATH", "models/nmt_model_en_te.pt")
    )  # Example: PyTorch model
    LOCAL_TTS_MODEL_PATH: str = Field(
        default=os.getenv("LOCAL_TTS_MODEL_PATH", "models/tts_model.pth")
    )  # Example: Coqui TTS model

    # Ollama settings (if you integrate it for LLM tasks)
    OLLAMA_API_BASE_URL: str = Field(default=os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434/api"))
    OLLAMA_MODEL_NAME: str = Field(default=os.getenv("OLLAMA_MODEL_NAME", "llama3"))  # Example model name

    # Security settings
    JWT_SECRET: str = Field(default="d3b07384d113edec49eaa6238ad5ff00")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    jwt_secret: str = "supersecret"
    jwt_expires_in: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
