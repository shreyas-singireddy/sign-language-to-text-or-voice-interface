from pydantic import BaseModel, Field


class AlphabetPredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted character or digit (A-Z, 0-9)")
    confidence: float = Field(..., description="Confidence score [0.0 - 1.0]")
    alternatives: list[str] = Field(default_factory=list, description="Top alternative candidate predictions")


class WordPredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted word label (e.g. HELLO)")
    confidence: float = Field(..., description="Inference confidence score [0.0 - 1.0]")


class SentencePredictionResponse(BaseModel):
    prediction: str = Field(..., description="Decoded continuous sentence phrase")
    confidence: float = Field(..., description="Combined sequence decoding confidence score [0.0 - 1.0]")
