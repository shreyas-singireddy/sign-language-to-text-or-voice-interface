# Feature 001: AI Sign Explanation Engine

**Spec ID:** FEAT-001  
**Status:** Active  
**Owner:** @signbridge-team  
**Last Updated:** 2026-06-13

---

## 1. Overview

The AI Sign Explanation Engine is an intelligent post-detection layer that enriches raw gesture classifications with contextual information. After a sign is detected by the vision pipeline, this engine explains its meaning, shows confidence scores, highlights possible misclassifications, and suggests related signs.

This dramatically improves accessibility by helping users — especially learners — understand *why* a sign was recognised and what variations exist.

## 2. Goals & Non-Goals

### Goals
- **Must Have:** Display the detected sign label and confidence score in the UI.
- **Must Have:** Provide a plain-language explanation of the sign's meaning.
- **Must Have:** List the top-3 similar signs with Levenshtein/semantic distance.
- **Should Have:** Explain potential misclassification causes (lighting, angle, speed).
- **Nice to Have:** Link to animated demonstration of the correct gesture.

### Non-Goals
- Does not perform real-time grammar correction (handled by `translation.grammar_fixer`).
- Does not train or fine-tune the underlying classifier.

## 3. User Stories

| ID | As a … | I want to … | So that … |
|----|--------|-------------|-----------|
| US-001-1 | deaf user | see which sign was detected | I can confirm the system understood me |
| US-001-2 | ASL learner | understand the meaning of detected signs | I can learn as I communicate |
| US-001-3 | support worker | see confidence scores | I can decide whether to repeat the gesture |

## 4. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001-1 | Engine SHALL return sign label, confidence (0–1), and top-3 alternatives | P0 |
| FR-001-2 | Engine SHALL provide a human-readable explanation string ≤ 200 chars | P0 |
| FR-001-3 | Engine SHALL classify misclassification risk as LOW/MEDIUM/HIGH | P1 |
| FR-001-4 | Engine SHALL suggest similar signs with similarity score | P1 |

## 5. Non-Functional Requirements

- **Latency:** Explanation generation ≤ 100 ms (CPU-only fallback mode).
- **Offline Support:** Must function without internet connectivity (LLM fallback to rule-based).
- **Accessibility:** Output text must comply with WCAG 2.1 AA reading level.

## 6. Architecture

### Components Affected
- `ai_engine/ai_agent/llm_engine.py` — LLM/fallback routing
- `ai_engine/ai_agent/error_detection.py` — Misclassification detection
- `backend/app/api/v1/ai_agent.py` — REST endpoint `/api/v1/ai-agent/explain`

### Data Models
- Input: `GestureExplanationRequest { sign_label: str, confidence: float, landmarks: list }`
- Output: `GestureExplanationResponse { explanation: str, similar_signs: list, misclassification_risk: str }`

### Third-Party Dependencies
- `google-generativeai` (optional, LLM backend)
- `rapidfuzz` (sign similarity computation)

## 7. Security & Privacy

- Gesture frames are NOT sent to external APIs in default mode.
- LLM requests in cloud mode send only the sign label string (no biometric data).
- No user PII is stored in explanation logs.

## 8. Testing Strategy

| Type | Target | Tool | Coverage Target |
|------|--------|------|----------------|
| Unit | `llm_engine.explain_sign()` | pytest | 85% |
| Unit | `error_detection.calculate_angle()` | pytest | 90% |
| Integration | `POST /api/v1/ai-agent/explain` | pytest + httpx | 80% |
| Manual | Real-world gesture capture | Human reviewer | N/A |

## 9. Acceptance Criteria

- [ ] `/api/v1/ai-agent/explain` returns 200 with valid JSON for all known signs.
- [ ] Confidence scores are in [0.0, 1.0] range.
- [ ] Similar signs list contains 1–3 entries.
- [ ] All unit tests pass with coverage ≥ 80%.
- [ ] No MEDIUM or HIGH security findings.

## 10. References

- [Architecture Spec](../../templates/architecture-spec.md)
- [Tasks](./tasks.md)
- [Design](./design.md)
- [Constitution](../../constitution.md)
