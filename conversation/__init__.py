"""
SignBridge AI — Layer 7: Conversation Platform Package
Provides session-based conversation memory, dialogue management,
message threading, and emotion tone detection for sign language communication.
"""
from conversation.dialogue_manager import DialogueManager, dialogue_manager
from conversation.session import ConversationSession

__all__ = ["DialogueManager", "dialogue_manager", "ConversationSession"]
