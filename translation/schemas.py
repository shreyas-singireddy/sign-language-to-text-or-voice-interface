"""
SignBridge AI — Layer 5: Translation Engine Schemas
Pydantic models for all translation I/O contracts.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TranslationProvider(str, Enum):
    """Enumeration of all supported translation providers."""
    RULE_BASED = "rule_based"
    GOOGLE = "google"
    LOCAL_LLM = "local_llm"


class TranslationRequest(BaseModel):
    """Input schema for a translation request from Layer 4."""
    recognized_signs: List[str] = Field(
        ...,
        description="Ordered list of recognized sign tokens from Layer 4",
        min_length=1
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Aggregate confidence score from Layer 4 gesture predictor"
    )
    target_language: str = Field(
        default="English",
        description="Target language for the final translated output"
    )
    provider: TranslationProvider = Field(
        default=TranslationProvider.RULE_BASED,
        description="Which translation provider backend to use"
    )
    context_window: Optional[List[str]] = Field(
        default=None,
        description="Previous translation outputs for context-aware grammar correction"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp from the source gesture recognition event"
    )


class GrammarAnalysis(BaseModel):
    """Detailed grammar analysis of a raw sign token sequence."""
    raw_tokens: List[str] = Field(description="Original sign tokens as received")
    normalized_tokens: List[str] = Field(description="Deduplicated and normalized tokens")
    subject_detected: bool = Field(description="Whether a subject pronoun was inferred")
    tense_inferred: str = Field(description="Inferred grammatical tense: present/past/future")
    sentence_type: str = Field(description="Declarative, interrogative, imperative, or exclamatory")
    complexity_score: float = Field(
        ge=0.0, le=1.0,
        description="Normalized complexity score of the token sequence (0=simple, 1=complex)"
    )


class TranslationResult(BaseModel):
    """Full translation result returned from the Translation Engine."""
    original_signs: List[str] = Field(description="Original recognized sign tokens")
    english_base: str = Field(description="Intermediate English grammar-corrected sentence")
    final_translation: str = Field(description="Final translation in the requested target language")
    target_language: str = Field(description="Language of the final translation")
    provider_used: TranslationProvider = Field(description="Which provider processed the translation")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall translation confidence")
    grammar_analysis: GrammarAnalysis = Field(description="Grammar analysis object for diagnostics")
    context_applied: bool = Field(description="Whether conversational context was applied")
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative phrasings of the same translation"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific metadata and diagnostics"
    )


class ContextEntry(BaseModel):
    """A single entry in the translation context window."""
    signs: List[str] = Field(description="Sign tokens for this turn")
    translation: str = Field(description="Final translated text for this turn")
    language: str = Field(description="Language used for this turn")
    turn_index: int = Field(description="Turn number in the conversation")
    timestamp: str = Field(description="ISO 8601 timestamp of this turn")


class ContextWindow(BaseModel):
    """Sliding context window for conversation-aware translation."""
    entries: List[ContextEntry] = Field(default_factory=list)
    max_turns: int = Field(default=10, description="Maximum turns to retain in context")
    session_id: str = Field(description="Unique session identifier")
