from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: str
    createdAt: datetime

    model_config = {"populate_by_name": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TranslationInput(BaseModel):
    imageData: str
    language: str = "English"


class TranslationRecord(BaseModel):
    id: str = Field(..., alias="_id")
    userId: str
    detectedGesture: str
    translatedText: str
    confidence: float
    timestamp: datetime

    model_config = {"populate_by_name": True}
