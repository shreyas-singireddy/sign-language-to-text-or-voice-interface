# Feature 001: AI Sign Explanation Engine — Design Document

**Spec ID:** FEAT-001  
**Last Updated:** 2026-06-13

---

## 1. System Design Overview

The AI Sign Explanation Engine sits between the gesture classifier output and the frontend display layer. It acts as an enrichment service that takes a raw classification result and produces a rich, user-friendly explanation object.

```
┌──────────────────────────────────────────────────────────────┐
│                    Gesture Pipeline                          │
│                                                              │
│  Camera → MediaPipe → Classifier → [AI Explanation Engine]  │
│                                           │                  │
│                           ┌───────────────┘                  │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │   LLM Engine           │                      │
│              │   (gemini / fallback)  │                      │
│              └────────────────────────┘                      │
│                           │                                  │
│              ┌────────────────────────┐                      │
│              │   Error Detector       │                      │
│              │   (angle analysis)     │                      │
│              └────────────────────────┘                      │
│                           │                                  │
│              ┌────────────────────────┐                      │
│              │   Sign Similarity      │                      │
│              │   (rapidfuzz)          │                      │
│              └────────────────────────┘                      │
│                           │                                  │
│              ┌────────────────────────┐                      │
│              │  ExplanationResponse   │                      │
│              └────────────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Diagram

```
INPUT: GestureClassification
  sign_label: "Hello"
  confidence: 0.91
  landmark_data: FrameLandmarkData

       │
       ▼
  LLM Engine
  ───────────
  if GOOGLE_API_KEY → Gemini API call
  else              → local SIGN_EXPLANATIONS dict lookup

       │
       ▼
  Error Detector
  ──────────────
  Compute joint angles from landmarks
  Compare against reference ranges
  Output: risk_level ∈ {LOW, MEDIUM, HIGH}

       │
       ▼
  Similarity Engine
  ─────────────────
  Levenshtein distance → top-3 similar signs
  Semantic embedding distance (optional)

       │
       ▼
OUTPUT: GestureExplanationResponse
  explanation: "Hello is a common greeting gesture..."
  confidence: 0.91
  misclassification_risk: "LOW"
  similar_signs: ["Hi", "Hey", "Wave"]
```

## 3. API Contract

### Request
```json
POST /api/v1/ai-agent/explain
Authorization: Bearer <jwt_token>

{
  "sign_label": "Hello",
  "confidence": 0.91,
  "session_id": "abc-123"
}
```

### Response
```json
{
  "sign_label": "Hello",
  "confidence": 0.91,
  "explanation": "Hello is a common ASL greeting. Wave open hand near head.",
  "misclassification_risk": "LOW",
  "similar_signs": ["Hi", "Hey", "Wave"],
  "processing_ms": 42
}
```

### Error Responses
| Code | Condition |
|------|-----------|
| 422 | Missing or invalid request fields |
| 401 | Missing or expired JWT token |
| 503 | LLM backend unavailable and no fallback dict entry |

## 4. Module Design

### 4.1 `llm_engine.py`

```python
class LLMEngine:
    def explain_sign(self, sign_label: str) -> str:
        """Return human-readable explanation for sign_label."""
        # 1. Check LRU cache
        # 2. Try Gemini API if key configured
        # 3. Fall back to SIGN_EXPLANATIONS dict
        # 4. Return generic placeholder if unknown
```

### 4.2 `error_detection.py`

```python
def calculate_angle(a: Point3D, b: Point3D, c: Point3D) -> float:
    """Compute angle at vertex b between vectors ba and bc."""

class ErrorDetector:
    def assess_risk(self, landmarks: FrameLandmarkData) -> str:
        """Assess gesture error risk: LOW | MEDIUM | HIGH."""
```

### 4.3 `learning_coach.py`

```python
class LearningCoach:
    def get_quiz(self, user_id: str) -> QuizQuestion:
        """Generate personalised quiz question based on error history."""

    def record_attempt(self, user_id: str, sign: str, correct: bool) -> None:
        """Record quiz attempt in offline or online DB."""
```

## 5. Database Schema (Offline Mode)

```json
// ai_engine/datasets/data/offline_learning_progress.json
{
  "user_id": {
    "signs_practiced": ["Hello", "Thank You"],
    "error_counts": {"Hello": 2},
    "quiz_scores": [{"date": "2026-06-13", "score": 0.85}]
  }
}
```

## 6. Performance Design

| Metric | Target | Strategy |
|--------|--------|----------|
| Explanation latency | ≤ 100 ms | LRU cache, async API calls |
| Similarity search | ≤ 10 ms | Pre-computed sign dictionary |
| Memory footprint | ≤ 50 MB | Dict-based fallback, no heavy models |

## 7. Observability

- All LLM calls logged with sign_label, latency, and provider used.
- Error detection risk distribution emitted to Streamlit telemetry dashboard.
- Cache hit rate tracked as `llm_cache_hit_rate` metric.

## 8. Future Enhancements

- Integrate video demonstration clips for each sign.
- Multilingual explanations using `src/locales/` i18n JSON files.
- Federated learning: aggregate error patterns across users (privacy-preserving).
