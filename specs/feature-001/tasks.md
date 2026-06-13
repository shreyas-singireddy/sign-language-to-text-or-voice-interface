# Feature 001: AI Sign Explanation Engine — Task Breakdown

**Feature:** FEAT-001  
**Sprint:** Sprint-01  
**Last Updated:** 2026-06-13

---

## Task List

| Task ID | Description | Status | Assignee | Points |
|---------|-------------|--------|----------|--------|
| TASK-001-1 | Implement `llm_engine.explain_sign()` with rule-based fallback | Done | @ai-team | 5 |
| TASK-001-2 | Implement `error_detection.calculate_angle()` for pose analysis | Done | @cv-team | 3 |
| TASK-001-3 | Create `POST /api/v1/ai-agent/explain` FastAPI endpoint | Done | @backend-team | 3 |
| TASK-001-4 | Add similar-sign suggestion logic with rapidfuzz | Done | @ai-team | 3 |
| TASK-001-5 | Write unit tests for llm_engine and error_detection | Done | @qa-team | 3 |
| TASK-001-6 | Integrate explanation panel in Streamlit dashboard | Done | @frontend-team | 2 |
| TASK-001-7 | Performance benchmark: ≤ 100 ms explanation latency | Done | @ai-team | 2 |

---

## TASK-001-1: LLM Engine with Fallback

**Status:** Done  
**File:** `ai_engine/ai_agent/llm_engine.py`

### Acceptance Criteria
- [x] Returns explanation string for any recognised sign label.
- [x] Falls back to rule-based dictionary if LLM is unavailable.
- [x] Response time ≤ 100 ms in fallback mode.

### Implementation Notes
- Uses `google-generativeai` when `GOOGLE_API_KEY` is set.
- Falls back to `SIGN_EXPLANATIONS` dict in offline mode.
- LRU cache prevents repeated API calls for same sign label.

---

## TASK-001-2: Error Detection Engine

**Status:** Done  
**File:** `ai_engine/ai_agent/error_detection.py`

### Acceptance Criteria
- [x] `calculate_angle()` returns angle in degrees from 3 landmark points.
- [x] `error_detector.detect()` classifies gesture error as LOW/MEDIUM/HIGH.
- [x] Unit tests cover all error categories.

---

## TASK-001-3: API Endpoint

**Status:** Done  
**File:** `backend/app/api/v1/ai_agent.py`

### Acceptance Criteria
- [x] `POST /api/v1/ai-agent/explain` returns 200 with explanation JSON.
- [x] Returns 422 for malformed requests.
- [x] JWT authentication enforced.

---

## Definition of Done (Feature Level)

- [x] All 7 tasks completed.
- [x] `ruff check .` passes.
- [x] `mypy .` passes (180 files, no issues).
- [x] `bandit -r .` passes (0 issues).
- [x] `vulture .` passes (0 dead code).
- [x] 229 tests pass, coverage = 80.84%.
- [x] Compliance validator = 100%.
