from config.logger import setup_logger

logger = setup_logger("ai_engine.translation")


class TranslationEngine:
    def __init__(self):
        # Basic mapping rules for sign-to-speech mapping
        self.phrase_dictionary = {
            ("HELLO",): "Hello!",
            ("HELLO", "PLEASE"): "Hello, please.",
            ("PLEASE", "HELP"): "Please help me.",
            ("SORRY", "NO"): "I am sorry, no.",
            ("YES",): "Yes.",
            ("NO",): "No.",
            ("THANKS",): "Thank you!",
            ("GOOD MORNING",): "Good morning!",
            ("GOOD NIGHT",): "Good night!",
            ("HELP",): "I need help.",
            ("SORRY",): "Sorry.",
        }

    def translate(self, gesture_sequence: list, language: str = "English") -> str:
        """
        Translates a sequence of gesture strings into a natural language sentence.
        """
        if not gesture_sequence:
            return ""

        # Remove consecutive duplicate tokens if any got past the sequence detector
        clean_sequence = []
        for token in gesture_sequence:
            if not clean_sequence or clean_sequence[-1] != token:
                clean_sequence.append(token)

        key = tuple(clean_sequence)

        # Search direct matches in sign phrase book
        if key in self.phrase_dictionary:
            base_translation = self.phrase_dictionary[key]
        else:
            # Fallback: Join and format tokens
            base_translation = " ".join(clean_sequence).capitalize() + "."

        # Translate output language from base (English) if requested
        # For scaffolding, we provide mock multilingual variations
        return self._apply_multilingual_mapping(base_translation, language)

    def _apply_multilingual_mapping(self, english_text: str, target_language: str) -> str:
        """
        Translates the English sentence into other supported languages.
        """
        if target_language == "English":
            return english_text

        # Basic mock translation maps for key phrases to show multi-language capability
        translations = {
            "Spanish": {
                "Hello!": "¡Hola!",
                "Please help me.": "Por favor ayúdame.",
                "Thank you!": "¡Gracias!",
                "Yes.": "Sí.",
                "No.": "No.",
                "I need help.": "Necesito ayuda.",
                "Sorry.": "Lo siento.",
                "Good morning!": "¡Buenos días!",
                "Good night!": "¡Buenas noches!",
            },
            "Hindi": {
                "Hello!": "नमस्ते!",
                "Please help me.": "कृपया मेरी मदद करें।",
                "Thank you!": "धन्यवाद!",
                "Yes.": "हाँ।",
                "No.": "नहीं।",
                "I need help.": "मुझे मदद चाहिए।",
                "Sorry.": "माफ़ कीजिये।",
                "Good morning!": "शुभ प्रभात!",
                "Good night!": "शुभ रात्रि!",
            },
            "Telugu": {
                "Hello!": "హలో!",
                "Please help me.": "దయచేసి నాకు సహాయం చేయండి.",
                "Thank you!": "ధన్యవాదాలు!",
                "Yes.": "అవును.",
                "No.": "కాదు.",
                "I need help.": "నాకు సహాయం కావాలి.",
                "Sorry.": "క్షమించండి.",
                "Good morning!": "శుభోదయం!",
                "Good night!": "శుభ రాత్రి!",
            },
        }

        # Query the dictionary
        lang_map = translations.get(target_language, {})
        if english_text in lang_map:
            return lang_map[english_text]

        # General translator stub message for unsupported languages or complex phrases
        logger.info(f"Target language '{target_language}' not fully mapped. Appending translation stub.")
        return f"[Translated to {target_language}]: {english_text}"


translation_engine = TranslationEngine()
