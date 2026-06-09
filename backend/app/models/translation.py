from dataclasses import dataclass
from datetime import datetime

@dataclass
class TranslationModel:
    userId: str
    detectedGesture: str
    translatedText: str
    confidence: float
    timestamp: datetime = datetime.utcnow()
