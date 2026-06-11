"""
SignBridge AI — Layer 7: Conversation Schemas
Pydantic models for all conversation platform data contracts.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class MessageRole(str, Enum):
    """Speaker role in the conversation."""
    SIGNER = "signer"       # The sign language user
    LISTENER = "listener"   # The hearing/reading counterpart
    SYSTEM = "system"       # System messages (notifications, errors)


class EmotionTone(str, Enum):
    """Detected emotional tone of a message."""
    NEUTRAL = "neutral"
    URGENT = "urgent"
    FRIENDLY = "friendly"
    DISTRESSED = "distressed"
    GRATEFUL = "grateful"
    CONFUSED = "confused"


class Message(BaseModel):
    """A single message in a conversation thread."""
    id: str = Field(description="Unique message identifier")
    role: MessageRole = Field(description="Who produced this message")
    original_signs: List[str] = Field(
        default_factory=list,
        description="Raw sign tokens (empty for listener/system messages)"
    )
    text: str = Field(description="Final translated or typed text")
    language: str = Field(default="English", description="Language of the text")
    emotion: EmotionTone = Field(default=EmotionTone.NEUTRAL, description="Detected emotional tone")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Translation confidence")
    timestamp: datetime = Field(description="Message creation time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata")


class ConversationThread(BaseModel):
    """Ordered sequence of messages in a conversation session."""
    session_id: str = Field(description="Unique session identifier")
    messages: List[Message] = Field(default_factory=list, description="All messages in order")
    started_at: datetime = Field(description="When this conversation began")
    language: str = Field(default="English", description="Primary conversation language")
    participant_count: int = Field(default=2, description="Number of participants")
    is_active: bool = Field(default=True, description="Whether the conversation is ongoing")


class DialogueTurn(BaseModel):
    """A complete dialogue turn from sign input to translated response."""
    turn_index: int = Field(description="Turn number in the conversation")
    input_signs: List[str] = Field(description="Sign tokens received")
    english_intermediate: str = Field(description="Intermediate English translation")
    final_text: str = Field(description="Final translated text")
    language: str = Field(description="Target language")
    emotion: EmotionTone = Field(description="Detected tone")
    confidence: float = Field(ge=0.0, le=1.0)
    response_suggestion: Optional[str] = Field(
        default=None,
        description="Suggested response for the hearing participant"
    )
    timestamp: datetime = Field(description="Turn timestamp")


class SessionSummary(BaseModel):
    """Summary of a completed or active conversation session."""
    session_id: str
    total_turns: int
    total_messages: int
    languages_used: List[str]
    duration_seconds: Optional[float]
    dominant_emotion: EmotionTone
    started_at: datetime
    last_activity: Optional[datetime]
    sign_tokens_processed: int
