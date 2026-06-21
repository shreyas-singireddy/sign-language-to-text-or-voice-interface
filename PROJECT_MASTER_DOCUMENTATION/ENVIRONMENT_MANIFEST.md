# ENVIRONMENT MANIFEST - SignBridge AI Reconstruction Blueprint

This document details the configuration properties, folder permissions, path targets, and environment variables of the SignBridge AI application.

---

## 1. System Requirements

*   **Operating System**: Windows (tested and validated under Windows 10/11), macOS, or Linux.
*   **Python Runtime**: `Python 3.12` is recommended.
*   **Hardware Devices**:
    *   *Camera*: Integrated webcam or external USB camera accessible via OpenCV (typically device index `0`).
    *   *CPU*: Dual-core processor with minimum 8GB RAM (required for running holistic real-time neural network tracking at >25 FPS).
    *   *GPU*: Nvidia CUDA (Optional, falls back to CPU execution automatically).

---

## 2. Directory Configurations

The application initializes the following folders on startup:

*   **Model Weights Directory**: `assets/models/`
    *   *Role*: Stores PyTorch checkpoints (`.pt`) for both the fingerspelling MLP models and sequential models.
*   **Model Catalog Registry**: `assets/models/registry/`
    *   *Role*: Houses `registry_metadata.json` which tracks active versions and rollback targets.
*   **Recording Paths**: `data/recordings/`
    *   *Role*: Stores raw coordinates files captured during recording sessions.
*   **Exports Target**: `data/exports/`
    *   *Role*: Output directory for exported formats (CSV, Parquet, JSON).
*   **Dataset Storage**: `ai_engine/datasets/data/`
    *   *Role*: Stores local configuration index JSONs and the offline history fallback file (`offline_history.json`).

---

## 3. Environment Variables Configuration (`.env`)

Save the following configuration inside `.env` in either the project root or the `backend/` directory:

```ini
# Application configuration
PROJECT_NAME="SignBridge AI"
WEBCAM_SOURCE=0

# Database configurations
MONGO_URI="mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
DB_NAME="signbridge_ai"

# MediaPipe configuration thresholds
MP_STATIC_IMAGE_MODE=False
MP_MAX_NUM_HANDS=2
MP_MIN_DETECTION_CONFIDENCE=0.5
MP_MIN_TRACKING_CONFIDENCE=0.5

# Inference Thresholds
GESTURE_CONFIDENCE_THRESHOLD=0.7
SEQUENCE_BUFFER_SIZE=30

# Backend Authentication parameters
JWT_SECRET="<SET_IN_ENVIRONMENT>"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=11520
```

---

## 4. Behavior Alterations & Fallbacks for Missing Variables

*   **Missing `MONGO_URI`**:
    *   *Behavior change*: The application outputs: `MONGO_URI not configured. Operating in offline/mock mode.`
    *   *Fallback*: Database writes redirect to `ai_engine/datasets/data/offline_history.json`.
*   **Missing `.env` file**:
    *   *Behavior change*: All settings default to standard configurations (e.g. webcam `0`, MongoDB `offline` mode, and MediaPipe confidence `0.5`).
*   **Missing model weights (`.pt`)**:
    *   *Behavior change*: The application falls back to **synthetic sequence feature generation**, allowing the user interface to compile and function without crashing.
