# [System/Module] Architecture Specification

**Spec ID:** ARCH-XXX  
**Status:** Proposed | Active | Deprecated  
**Owner:** @architect  
**Last Updated:** YYYY-MM-DD

---

## 1. Purpose

Describe the architectural concern, what system or layer this document governs, and why this design was chosen.

## 2. System Context

```
┌────────────────────────────────────────────────────────┐
│                    SignBridge AI                        │
│  ┌──────────┐   ┌──────────┐   ┌────────────────────┐ │
│  │ Frontend │ → │ FastAPI  │ → │  AI Engine (CV/ML) │ │
│  │ React/   │   │ Backend  │   │  MediaPipe + PyTorch│ │
│  │ Streamlit│   │          │   └────────────────────┘ │
│  └──────────┘   └──────────┘                          │
└────────────────────────────────────────────────────────┘
```

## 3. Design Decisions

| Decision | Choice | Rationale | Alternatives Rejected |
|----------|--------|-----------|----------------------|
| Database | MongoDB | Schema-flexible, document-oriented | PostgreSQL (rigid schema) |
| ML Runtime | MediaPipe 0.10.14 | Proven hand/face tracking accuracy | OpenCV only (no landmark detection) |

## 4. Component Breakdown

### 4.1 Frontend Layer
- **React + Vite:** Production UI for end-users.
- **Streamlit:** Developer console and telemetry dashboard.

### 4.2 Backend Layer
- **FastAPI:** Async REST API server, JWT auth, WebSocket.
- **Uvicorn:** ASGI server.

### 4.3 AI Engine
- **MediaPipe Holistic:** Landmark extraction (hands, face, pose).
- **Sequence Classifier:** Temporal gesture recognition.
- **Translation Engine:** Sign-to-text mapping with grammar correction.

### 4.4 Data Layer
- **MongoDB Atlas:** User sessions, translation history.
- **Offline Mode:** JSON-backed fallback when DB is unavailable.

## 5. Data Flow

```
Camera Frame
  → MediaPipe Landmark Extraction
  → Feature Normalization
  → Sequence Buffer (N=30 frames)
  → Gesture Classifier (PyTorch / heuristic)
  → Translation Engine
  → gTTS / Browser TTS
  → Frontend Display
```

## 6. Cross-Cutting Concerns

- **Security:** All API routes require JWT bearer tokens (except /auth).
- **Logging:** Structured logging via `logging` module with UTC timestamps.
- **Configuration:** Environment variables loaded from `.env` (see `.env.example`).
- **Observability:** Telemetry metrics emitted to Streamlit dashboard.

## 7. Scalability Considerations

- FastAPI supports horizontal scaling behind a load balancer.
- MongoDB Atlas auto-sharding handles write throughput.
- AI Engine is CPU-bound; GPU acceleration is an optional upgrade.

## 8. Security Architecture

- Input frames are NOT persisted by default.
- JWT tokens expire after configurable TTL.
- Secrets injected via environment variables, never hardcoded.
- Bandit + Semgrep enforced in CI.

## 9. Dependency Constraints

| Package | Pinned Version | Reason |
|---------|---------------|--------|
| mediapipe | 0.10.14 | Protobuf compatibility |
| protobuf | 4.25.9 | Matches mediapipe binary ABI |
| starlette | 0.37.2 | FastAPI 0.111.1 compatibility |

## 10. Verification Plan

- [ ] All CI stages green on `main`.
- [ ] Architecture diagram matches live codebase (reviewed quarterly).
- [ ] Performance benchmarks documented in `DETECTION_AUDIT.md`.

## 11. References

- [constitution.md](../constitution.md)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [MediaPipe docs](https://mediapipe.dev/)
