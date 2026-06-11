# Spec-Kit: Live Translation Engine

## 1. Purpose
The Live Translation Engine accepts streams of classified gesture labels, groups them, applies grammar parsing rules, and translates the consolidated statements into 16 target languages.

## 2. Requirements
- **REQ-LT-001**: Translate raw sign word sequences into complete sentences.
- **REQ-LT-002**: Fix grammar irregularities (e.g. converting "WATER WANT" to "I want water.").
- **REQ-LT-003**: Output translation text in 16 supported languages.

## 3. Architecture
- **Translation Module**: Local Rule-Based translation tables + Google Translate API Adapter fallbacks.
- **Grammar Engine**: Local grammatical normalizer.
- **Output**: JSON payload with `translatedText`, `speechLang`, and `confidence`.

## 4. Acceptance Criteria
- Output sentences must start with a capital letter and end with a punctuation mark.
- Translations must map correctly to the selected language locale code.

## 5. Performance Targets
- Translation response latency: <= 100ms.
- Support 16 target language locales.

## 6. Security Considerations
- JWT Bearer tokens must be validated before allowing calls to the translation API.

## 7. Risks
- Network timeouts can disrupt Google Translate API requests. The system must fall back to local rule-based dictionaries when offline.

## 8. Test Cases
- **Test-LT-1**: Verify translation output for Spanish and Hindi.
- **Test-LT-2**: Verify offline fallback behavior when the internet is simulated as disconnected.

## 9. Verification Procedures
1. Run translation tests:
   ```bash
   pytest tests/test_translation.py
   ```
