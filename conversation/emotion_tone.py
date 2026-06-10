"""
SignBridge AI — Layer 7: Emotion Tone Detector
Classifies the emotional tone of a sign sequence or translated text
to enable appropriate response suggestions and UI adjustments.
"""
from typing import List, Dict
from conversation.schemas import EmotionTone
from config.logger import setup_logger

logger = setup_logger("conversation.emotion_tone")

# Token sets mapped to emotion categories
EMOTION_TOKEN_MAP: Dict[EmotionTone, List[str]] = {
    EmotionTone.URGENT: [
        "EMERGENCY", "SOS", "DANGER", "FIRE", "HELP", "CALL", "POLICE",
        "AMBULANCE", "DOCTOR", "HURRY", "NOW", "FAST", "CRITICAL",
        "PAIN", "HURT", "CHEST", "BREATHE", "FALL", "STUCK", "TRAPPED"
    ],
    EmotionTone.DISTRESSED: [
        "SORRY", "SAD", "CRY", "SCARED", "AFRAID", "LOST", "CONFUSED",
        "DON'T KNOW", "ALONE", "HELP ME", "PLEASE", "NEED", "WORRY",
        "BAD", "WRONG", "PROBLEM", "TROUBLE", "DIZZY", "SICK"
    ],
    EmotionTone.GRATEFUL: [
        "THANK", "THANKS", "THANK YOU", "APPRECIATE", "GOOD", "GREAT",
        "WONDERFUL", "HAPPY", "LOVE", "BEST", "NICE", "PERFECT",
        "AMAZING", "WONDERFUL", "EXCELLENT"
    ],
    EmotionTone.FRIENDLY: [
        "HELLO", "HI", "GOOD MORNING", "GOOD NIGHT", "HOW ARE YOU",
        "NICE", "MEET", "WELCOME", "BYE", "GOODBYE", "PLEASE",
        "FRIEND", "FAMILY", "LOVE", "CARE", "HAPPY"
    ],
    EmotionTone.CONFUSED: [
        "WHAT", "WHERE", "WHY", "HOW", "WHO", "WHEN", "UNDERSTAND",
        "NOT UNDERSTAND", "REPEAT", "AGAIN", "EXPLAIN", "SLOW",
        "HELP EXPLAIN", "CONFUSED", "MEAN", "LOST"
    ],
}

# Text phrase patterns mapped to emotion
EMOTION_TEXT_PATTERNS: Dict[EmotionTone, List[str]] = {
    EmotionTone.URGENT: [
        "emergency", "danger", "help me", "call police", "call ambulance",
        "need doctor", "chest pain", "cannot breathe", "can't breathe",
        "immediate", "right now", "hurry", "sos"
    ],
    EmotionTone.DISTRESSED: [
        "i am lost", "i don't know", "i am scared", "i am afraid",
        "please help", "i am alone", "something is wrong", "i am sick"
    ],
    EmotionTone.GRATEFUL: [
        "thank you", "i appreciate", "that's great", "wonderful", "perfect"
    ],
    EmotionTone.FRIENDLY: [
        "hello", "good morning", "good evening", "good night", "nice to meet",
        "how are you", "goodbye", "have a great"
    ],
    EmotionTone.CONFUSED: [
        "i don't understand", "i do not understand", "can you repeat",
        "what does that mean", "please explain", "i'm confused"
    ],
}

# Emotion → response suggestion templates
RESPONSE_SUGGESTIONS: Dict[EmotionTone, str] = {
    EmotionTone.URGENT: "🚨 Urgent situation detected. Respond quickly or call emergency services.",
    EmotionTone.DISTRESSED: "💙 This person needs reassurance. Respond calmly and offer assistance.",
    EmotionTone.GRATEFUL: "😊 They're expressing gratitude. A warm response is appropriate.",
    EmotionTone.FRIENDLY: "👋 Casual greeting. Respond in a friendly, welcoming manner.",
    EmotionTone.CONFUSED: "❓ They need clarification. Speak clearly and offer to repeat or simplify.",
    EmotionTone.NEUTRAL: "💬 Neutral communication. Respond naturally.",
}


class EmotionToneDetector:
    """
    Classifies the emotional tone of sign language input.
    Uses a token-matching approach for real-time detection without ML models.
    Priority order: URGENT > DISTRESSED > CONFUSED > GRATEFUL > FRIENDLY > NEUTRAL
    """

    PRIORITY_ORDER = [
        EmotionTone.URGENT,
        EmotionTone.DISTRESSED,
        EmotionTone.CONFUSED,
        EmotionTone.GRATEFUL,
        EmotionTone.FRIENDLY,
        EmotionTone.NEUTRAL,
    ]

    def detect_from_tokens(self, tokens: List[str]) -> EmotionTone:
        """
        Detect emotion from a list of sign language tokens.

        Args:
            tokens: Normalized sign token list (uppercase)

        Returns:
            Detected EmotionTone
        """
        token_set = {t.upper() for t in tokens}

        for emotion in self.PRIORITY_ORDER:
            if emotion == EmotionTone.NEUTRAL:
                return EmotionTone.NEUTRAL
            known_tokens = {t.upper() for t in EMOTION_TOKEN_MAP.get(emotion, [])}
            if token_set & known_tokens:
                logger.debug(f"Emotion detected from tokens: {emotion.value}")
                return emotion

        return EmotionTone.NEUTRAL

    def detect_from_text(self, text: str) -> EmotionTone:
        """
        Detect emotion from translated English text.

        Args:
            text: English translation text

        Returns:
            Detected EmotionTone
        """
        lower_text = text.lower()

        for emotion in self.PRIORITY_ORDER:
            if emotion == EmotionTone.NEUTRAL:
                return EmotionTone.NEUTRAL
            patterns = EMOTION_TEXT_PATTERNS.get(emotion, [])
            if any(p in lower_text for p in patterns):
                logger.debug(f"Emotion detected from text: {emotion.value}")
                return emotion

        return EmotionTone.NEUTRAL

    def detect(self, tokens: List[str], text: str) -> EmotionTone:
        """
        Detect emotion using both tokens and text, tokens take priority.

        Args:
            tokens: Sign token list
            text: Translated text

        Returns:
            Most appropriate EmotionTone
        """
        token_emotion = self.detect_from_tokens(tokens)
        if token_emotion != EmotionTone.NEUTRAL:
            return token_emotion
        return self.detect_from_text(text)

    def get_response_suggestion(self, emotion: EmotionTone) -> str:
        """
        Get a response suggestion for the hearing participant based on detected emotion.

        Args:
            emotion: Detected emotion tone

        Returns:
            Response suggestion string for display in the UI
        """
        return RESPONSE_SUGGESTIONS.get(emotion, RESPONSE_SUGGESTIONS[EmotionTone.NEUTRAL])

    def get_ui_color(self, emotion: EmotionTone) -> str:
        """
        Get the Bauhaus card color accent for a given emotion.

        Args:
            emotion: Emotion tone

        Returns:
            CSS class name: 'card-red', 'card-blue', 'card-yellow', or ''
        """
        color_map = {
            EmotionTone.URGENT: "card-red",
            EmotionTone.DISTRESSED: "card-blue",
            EmotionTone.GRATEFUL: "card-yellow",
            EmotionTone.FRIENDLY: "card-blue",
            EmotionTone.CONFUSED: "card-yellow",
            EmotionTone.NEUTRAL: "",
        }
        return color_map.get(emotion, "")


emotion_detector = EmotionToneDetector()
