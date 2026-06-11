# PROJECT INVENTORY - SignBridge AI Reconstruction Blueprint

This document details the file-by-file inventory of the SignBridge AI codebase, mapping each directory, explaining file responsibilities, listing size, and specifying import dependencies and criticality ratings.

---

## 1. Project Directory Structure

```text
sign-language-to-text-or-voice-translator/
├── accessibility/           # UI accessibility & screen reader integration
├── ai_engine/               # Core computer vision, tracking, and deep learning models
│   ├── computer_vision/     # MediaPipe camera abstraction
│   ├── dataset_manager/     # Dynamic coordinate recorder
│   ├── datasets/            # Offline configuration JSONs and templates
│   ├── exporters/           # Flat coordinates format export utility
│   ├── feature_extractor/   # Key landmark coordinate selection
│   ├── gesture_recognition/ # PyTorch gestures classifiers (LSTM, TCN, etc.)
│   ├── landmark_processor/  # EMA coordinate smoothing filters
│   ├── motion_analysis/     # Velocity & kinematic trackers
│   ├── pipeline/            # End-to-end telemetry frames execution pipeline
│   ├── processing/          # Coordinate centering & normalizers
│   ├── services/            # Perception service orchestration layer
│   ├── telemetry/           # Tracking indicators (occlusion, stability)
│   ├── translation_engine/  # Mapping output token to translation modules
│   └── vision/              # Hand, pose, and face sub-detectors
├── analytics/               # System metrics collectors & HTML report builders
├── app/                     # Multi-page Streamlit portal
│   └── pages/               # Streamlit application layout pages
├── assets/                  # Model weights binaries & registry configurations
├── backend/                 # FastAPI server (Uvicorn) & telemetry web socket
├── communication/           # Real-time WebSocket relay and chat rooms
├── config/                  # Global settings, constants, and logging configuration
├── conversation/            # Context dialog managers & emotion tone analyzers
├── database/                # MongoDB Atlas connection manager & offline fallbacks
├── emergency/               # Panic word matching & alert notification dispatcher
├── frontend/                # Vite React app directory & main Streamlit overrides
├── multilingual/            # Internationalization, localizer, and RTL formatting
├── speech/                  # TTS (gTTS, browser Web Speech API) & STT (Whisper)
├── tests/                   # Scaffolding unit tests & system validations
└── translation/             # Grammar correctors & adapter pipelines
```

---

## 2. Core Python Source Code Registry

For a complete rebuild, the 207 files are classified below:

### 2.1 Configuration & Utilities Layer
*   **[CRITICAL] [config/config.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/config/config.py)** (2,194 bytes)
    *   *Purpose*: Loads environment variables, configures default parameters, and paths for datasets and model registry. Sets list of supported gestures and languages.
    *   *Imports*: `dotenv`, `pathlib`, `os`.
*   **[CRITICAL] [config/logger.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/config/logger.py)** (831 bytes)
    *   *Purpose*: Formats system output logs with timestamps and severity levels.
    *   *Imports*: `logging`, `sys`.
*   **[CRITICAL] [ai_engine/utils/config.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/utils/config.py)** (1,679 bytes)
    *   *Purpose*: Defines camera resolutions, detection thresholds, and exports folders using Pydantic.
    *   *Imports*: `pydantic`.

### 2.2 Ingest and Computer Vision Pipeline (`ai_engine/`)
*   **[CRITICAL] [ai_engine/services/perception_service.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/services/perception_service.py)** (11,955 bytes)
    *   *Purpose*: The primary interface combining camera frame read, holistic landmark detection, smoothing, motion metrics, and telemetry outputs.
    *   *Imports*: `mediapipe`, `cv2`, `ai_engine.vision.camera_manager`, `ai_engine.vision.hand_detector`, `ai_engine.vision.pose_detector`.
*   **[CRITICAL] [ai_engine/vision/camera_manager.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/camera_manager.py)** (4,958 bytes)
    *   *Purpose*: High-performance frame capture and resizing using OpenCV.
    *   *Imports*: `cv2`, `time`.
*   **[CRITICAL] [ai_engine/vision/hand_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/hand_detector.py)** (3,615 bytes)
    *   *Purpose*: Configures and runs MediaPipe hands tracking solutions.
    *   *Imports*: `mediapipe`, `numpy`.
*   **[CRITICAL] [ai_engine/vision/pose_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/pose_detector.py)** (3,095 bytes)
    *   *Purpose*: Extracts holistic bodily/shoulder skeletal nodes.
    *   *Imports*: `mediapipe`.
*   **[CRITICAL] [ai_engine/vision/face_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/face_detector.py)** (3,284 bytes)
    *   *Purpose*: Tracks facial expression indicators and pitch/yaw rotation.
    *   *Imports*: `mediapipe`.
*   **[CRITICAL] [ai_engine/landmark_processor/processor.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/landmark_processor/processor.py)** (3,538 bytes)
    *   *Purpose*: Runs Exponential Moving Average (EMA) to prevent coordinate jitter.
    *   *Imports*: `numpy`, `ai_engine.schemas.landmark_schema`.
*   **[CRITICAL] [ai_engine/processing/landmark_normalizer.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/processing/landmark_normalizer.py)** (2,918 bytes)
    *   *Purpose*: Subtracts root shoulder/wrist nodes and scales coordinate values.
    *   *Imports*: `numpy`.

### 2.3 Gesture Classification Layer (`ai_engine/gesture_recognition/`)
*   **[CRITICAL] [ai_engine/gesture_recognition/services/gesture_service.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/services/gesture_service.py)** (4,427 bytes)
    *   *Purpose*: Decodes coordinate buffers into classification tokens. Handles custom landmark saving and PyTorch training triggers.
    *   *Imports*: `torch`, `numpy`, `ai_engine.gesture_recognition.inference.predictor`.
*   **[CRITICAL] [ai_engine/gesture_recognition/inference/predictor.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/inference/predictor.py)** (10,295 bytes)
    *   *Purpose*: PyTorch session instance selector; evaluates loaded word models and alphabet MLPs.
    *   *Imports*: `torch`, `ai_engine.gesture_recognition.models.word_model`.
*   **[CRITICAL] [ai_engine/gesture_recognition/models/word_model.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/models/word_model.py)** (8,354 bytes)
    *   *Purpose*: Neural network modules definition supporting LSTM, BiLSTM, TCN, and Transformer.
    *   *Imports*: `torch`, `torch.nn`.
*   **[CRITICAL] [ai_engine/gesture_recognition/models/alphabet_model.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/models/alphabet_model.py)** (2,015 bytes)
    *   *Purpose*: MLP architecture for static fingerspelling classification.
    *   *Imports*: `torch`, `torch.nn`.
*   **[CRITICAL] [ai_engine/gesture_recognition/training/trainer.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/training/trainer.py)** (9,044 bytes)
    *   *Purpose*: Manages backpropagation loop, batching, and exports weight checkpoints.
    *   *Imports*: `torch`, `torch.utils.data`, `numpy`.

### 2.4 Translation & Dialogue Layers
*   **[CRITICAL] [translation/engine.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/translation/engine.py)** (11,618 bytes)
    *   *Purpose*: Converts token sequences into fluent sentences.
    *   *Imports*: `translation.providers.rule_based`, `translation.providers.google_adapter`, `translation.grammar_fixer`.
*   **[CRITICAL] [translation/providers/rule_based.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/translation/providers/rule_based.py)** (22,160 bytes)
    *   *Purpose*: Dictionary lookup mappings converting sign sequences (e.g. `['HELLO', 'THANKS']`) to standard expressions.
    *   *Imports*: `json`, `re`.
*   **[CRITICAL] [conversation/dialogue_manager.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/conversation/dialogue_manager.py)** (6,838 bytes)
    *   *Purpose*: Tracks thread states and maintains conversational memory slots.
    *   *Imports*: `conversation.session`, `conversation.emotion_tone`.

### 2.5 Speech Engine (TTS / STT)
*   **[CRITICAL] [speech/tts_engine.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/speech/tts_engine.py)** (7,046 bytes)
    *   *Purpose*: Dispatches voice outputs via gTTS provider or browser client overrides.
    *   *Imports*: `speech.providers.gtts_provider`, `speech.providers.browser_provider`.
*   **[CRITICAL] [speech/providers/gtts_provider.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/speech/providers/gtts_provider.py)** (8,857 bytes)
    *   *Purpose*: Synthesizes text to MP3 audios.
    *   *Imports*: `gtts`.

### 2.6 Database & Fallback Storage
*   **[CRITICAL] [database/mongodb.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/database/mongodb.py)** (2,870 bytes)
    *   *Purpose*: Singletone MongoDB client connection pool. Includes offline verification.
    *   *Imports*: `pymongo`.
*   **[CRITICAL] [app/services/database_service.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/services/database_service.py)** (6,590 bytes)
    *   *Purpose*: Fallback data handler writes local records in JSON when Mongo Atlas is offline.
    *   *Imports*: `json`, `database.mongodb`.

### 2.7 Analytics, Safety & Emergency
*   **[CRITICAL] [emergency/sos_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/emergency/sos_detector.py)** (6,456 bytes)
    *   *Purpose*: Identifies distress gestures (e.g. SOS pattern) or keywords.
    *   *Imports*: `emergency.emergency_phrases`.
*   **[CRITICAL] [emergency/alert_dispatcher.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/emergency/alert_dispatcher.py)** (5,540 bytes)
    *   *Purpose*: Issues emergency SMS alerts and desktop signals.
    *   *Imports*: `httpx`.
*   **[CRITICAL] [analytics/metrics_collector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/analytics/metrics_collector.py)** (9,214 bytes)
    *   *Purpose*: Calculates model latency drift and tracking stability statistics.
    *   *Imports*: `numpy`, `pandas`.

---

## 3. Streamlit Frontend Registry
*   **[CRITICAL] [app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/main.py)** (14,460 bytes)
    *   *Purpose*: Main application router with Bauhaus typography, styling injections, splash, and authentication logic.
*   **[CRITICAL] [app/pages/home.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/home.py)** (14,144 bytes)
    *   *Purpose*: Welcome interface containing pipeline layout cards.
*   **[CRITICAL] [frontend/pages/live_gesture_recognition.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/frontend/pages/live_gesture_recognition.py)** (18,930 bytes)
    *   *Purpose*: Visual control cockpit showing live webcam classifier feed, target metrics, alternatives, history table, and training options.
*   **[CRITICAL] [frontend/pages/live_vision_engine.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/frontend/pages/live_vision_engine.py)** (22,043 bytes)
    *   *Purpose*: Vision telemetry portal showing joint angles and recording parameters.
*   **[CRITICAL] [app/pages/live_translation.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/live_translation.py)** (6,469 bytes)
    *   *Purpose*: Output translation and voice profile dispatcher.
*   **[CRITICAL] [app/pages/training_studio.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/training_studio.py)** (5,063 bytes)
    *   *Purpose*: Training panel for custom gestures.
*   **[CRITICAL] [app/pages/communication_hub.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/communication_hub.py)** (13,382 bytes)
    *   *Purpose*: User chat rooms and messaging streams.
*   **[CRITICAL] [app/pages/analytics.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/analytics.py)** (10,364 bytes)
    *   *Purpose*: Renders history graphs and performance timelines.
*   **[CRITICAL] [app/pages/accessibility.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/accessibility.py)** (9,649 bytes)
    *   *Purpose*: Screen reader hints configurer and accessibility profiles.
*   **[CRITICAL] [app/pages/emergency.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/emergency.py)** (12,904 bytes)
    *   *Purpose*: Configuration panel for emergency contacts, SOS triggers, and warning triggers.
*   **[CRITICAL] [app/pages/settings.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/settings.py)** (3,750 bytes)
    *   *Purpose*: Webcam and backend configuration parameters.
*   **[CRITICAL] [app/pages/admin.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/pages/admin.py)** (4,106 bytes)
    *   *Purpose*: Administrator credentials and database resetting mechanisms.

---

## 4. Backend (FastAPI / WebSocket) Registry
*   **[CRITICAL] [backend/app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/backend/app/main.py)** (953 bytes)
    *   *Purpose*: FastAPI application starting routes.
*   **[CRITICAL] [backend/ws/telemetry_socket.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/backend/ws/telemetry_socket.py)** (1,714 bytes)
    *   *Purpose*: Feeds raw coordinates streams from external inputs.
*   **[CRITICAL] [backend/app/api/v1/auth.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/backend/app/api/v1/auth.py)** (2,306 bytes)
    *   *Purpose*: Verifies JSON web tokens.

---

## 5. File Classification Metrics

| File Path | Size (Bytes) | Category | Rebuild Criticality |
| :--- | :--- | :--- | :--- |
| `app/main.py` | 14,460 | Frontend Router | **CRITICAL** |
| `frontend/pages/live_gesture_recognition.py` | 18,930 | Streamlit Page | **CRITICAL** |
| `frontend/pages/live_vision_engine.py` | 22,043 | Streamlit Page | **CRITICAL** |
| `ai_engine/services/perception_service.py` | 11,955 | Vision Orchestrator | **CRITICAL** |
| `ai_engine/gesture_recognition/services/gesture_service.py` | 4,427 | Gestures Orchestrator | **CRITICAL** |
| `ai_engine/gesture_recognition/inference/predictor.py` | 10,295 | Deep Inference | **CRITICAL** |
| `database/mongodb.py` | 2,870 | DB Adapter | **CRITICAL** |
| `config/config.py` | 2,194 | Global Config | **CRITICAL** |
| `tests/test_systems.py` | 18,828 | Automated Test | **OPTIONAL** |
| `tests/test_gesture_recognition.py` | 7,986 | Automated Test | **OPTIONAL** |
| `backend/Dockerfile` | 229 | Container Setup | **UNUSED** (local run preferred) |
| `frontend/Dockerfile` | 227 | Container Setup | **UNUSED** (local run preferred) |
| `docker-compose.yml` | 348 | Multi-container Orchestrator | **UNUSED** (local run preferred) |
| `backend/app/tests/conftest.py` | 238 | Test Configuration | **OPTIONAL** |
| `frontend/dist/index.html` | 501 | Static Asset | **OPTIONAL** (Vite build output) |
| `frontend/dist/assets/index-ClAc4or7.css` | 10,151 | Static Asset | **OPTIONAL** (Vite build output) |
| `frontend/dist/assets/index-DS90qF14.js` | 165,905 | Static Asset | **OPTIONAL** (Vite build output) |
