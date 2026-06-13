import sys
from pathlib import Path

# Add project root to sys.path to allow imports from database and ai_engine
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from fastapi import APIRouter, status
from pydantic import BaseModel

from ai_engine.ai_agent.error_detection import error_detector
from ai_engine.ai_agent.learning_coach import learning_coach
from ai_engine.ai_agent.llm_engine import llm_engine
from ai_engine.ai_agent.rag_engine import rag_engine
from ai_engine.schemas.landmark_schema import (
    FaceTelemetryData,
    FrameLandmarkData,
    HandTelemetryData,
    PoseTelemetryData,
)

router = APIRouter()

# --- REQUEST / RESPONSE SCHEMAS ---

class ExplainRequest(BaseModel):
    detected_sign: str
    confidence: float = 1.0
    language: str = "English"

class ConversationAssistRequest(BaseModel):
    detected_phrase: str
    language: str = "English"

class LearningCoachRequest(BaseModel):
    phone: str
    language: str = "English"
    num_questions: int = 3

class ErrorDetectRequest(BaseModel):
    target_sign: str
    landmarks_flat: list[float] = [] # Optional flat list of landmarks coordinates

class RAGAskRequest(BaseModel):
    question: str
    top_k: int = 3

# --- API ENDPOINTS ---

@router.post("/explain", status_code=status.HTTP_200_OK)
async def explain_sign(req: ExplainRequest):
    prompt = (
        f"Explain the detected sign '{req.detected_sign}'. "
        f"The model detected it with a confidence score of {req.confidence * 100}%. "
        f"Format your response in the language '{req.language}'. "
        "Highlight its meaning, typical context, potential misclassifications with similar signs, "
        "and concrete suggestions to make the sign more clearly."
    )
    system_prompt = "You are an expert Sign Language Explainer and Accessibility Assistant."

    explanation = llm_engine.generate_completion(prompt, system_prompt=system_prompt)
    return {
        "detected_sign": req.detected_sign,
        "confidence": req.confidence,
        "language": req.language,
        "explanation": explanation
    }

@router.post("/conversation-assist", status_code=status.HTTP_200_OK)
async def conversation_assist(req: ConversationAssistRequest):
    prompt = (
        f"The user just signed the following phrase: '{req.detected_phrase}'. "
        f"Provide conversational suggestions, next-phrase predictions, and smart auto-complete actions. "
        f"Format your response directly in the language '{req.language}'."
    )
    system_prompt = "You are a Conversational Agent for deaf and hard-of-hearing users."

    suggestions = llm_engine.generate_completion(prompt, system_prompt=system_prompt)
    return {
        "detected_phrase": req.detected_phrase,
        "language": req.language,
        "suggestions": suggestions
    }

@router.post("/learning-coach", status_code=status.HTTP_200_OK)
async def get_learning_quiz(req: LearningCoachRequest):
    quiz_data = learning_coach.generate_quiz(
        phone=req.phone,
        lang_name=req.language,
        num_questions=req.num_questions
    )
    challenge_data = learning_coach.get_daily_challenge(
        phone=req.phone,
        lang_name=req.language
    )

    return {
        "phone": req.phone,
        "language": req.language,
        "quiz": quiz_data,
        "daily_challenge": challenge_data
    }

@router.post("/error-detect", status_code=status.HTTP_200_OK)
async def detect_errors(req: ErrorDetectRequest):
    frame_lms = FrameLandmarkData(
        timestamp=0.0,
        left_hand=HandTelemetryData(present=False, landmarks=[]),
        right_hand=HandTelemetryData(present=False, landmarks=[]),
        pose=PoseTelemetryData(present=False, landmarks=[]),
        face=FaceTelemetryData(present=False, landmarks=[])
    )

    # If flat landmarks list is passed (size 1662), populate FrameLandmarkData structure
    if len(req.landmarks_flat) == 1662:
        from ai_engine.services.perception_service import perception_service
        try:
            perception_service._update_from_flat_landmarks(frame_lms, np.array(req.landmarks_flat))
        except Exception:
            pass # fallback to mock defaults

    feedback = error_detector.detect_errors(frame_lms, req.target_sign)
    return feedback

@router.post("/rag-ask", status_code=status.HTTP_200_OK)
async def rag_ask(req: RAGAskRequest):
    context = rag_engine.retrieve_context(req.question, top_k=req.top_k)

    if not context:
        context = "No relevant documentation found in the master folder."

    prompt = (
        f"Answer the user's question: '{req.question}'\n\n"
        f"Use the following documentation context to compile your answer:\n{context}\n\n"
        "Ensure your response is clear, accurate, and highlights the technical or usage details."
    )
    system_prompt = "You are a SignBridge AI Knowledge Base Assistant built on project documentation."

    answer = llm_engine.generate_completion(prompt, system_prompt=system_prompt)
    return {
        "question": req.question,
        "answer": answer,
        "has_context": bool(context)
    }
