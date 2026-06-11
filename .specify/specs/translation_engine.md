# Spec-Kit: Translation Engine

## 1. Overview & Objectives
The Translation Engine maps classified gestures to natural language text in multiple target languages, matching grammatical conventions and locale requirements.

## 2. Requirements & Traceability
- **REQ-TR-001**: Must map English gesture keys (e.g. "HELLO") to one of the 16 supported languages.
- **REQ-TR-002**: Must maintain a local translation table for offline dictionary mapping.
- **REQ-TR-003**: Output must format the translation in a structured response containing the raw gesture, translated text, and language code.

## 3. Interface Definitions
```python
class TranslationEngine:
    def translate(self, gesture: str, target_lang: str) -> dict:
        """Translates a raw gesture to the target language.
        Returns:
            dict containing translatedText, language, and speechLang.
        """
        pass
```

## 4. Verification Plan
- **Test-TR-001**: Checked in `tests/test_translation.py` asserting translation accuracy for all 16 supported languages.
