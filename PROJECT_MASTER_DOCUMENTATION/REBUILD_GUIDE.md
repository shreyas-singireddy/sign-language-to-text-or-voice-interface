# REBUILD GUIDE - SignBridge AI Reconstruction Blueprint

This document provides step-by-step instructions for another AI agent to reconstruct the SignBridge AI application from scratch.

---

## Step 1: Directory Structure Setup

Create the directory structure:

```bash
mkdir -p config ai_engine/vision ai_engine/landmark_processor ai_engine/processing ai_engine/gesture_recognition/models ai_engine/gesture_recognition/inference ai_engine/gesture_recognition/services ai_engine/gesture_recognition/training ai_engine/gesture_recognition/storage database app/pages frontend/pages backend/app/core backend/app/api/v1 backend/ws assets/models/registry data/recordings data/exports tests multilingual speech/providers translation/providers
```

---

## Step 2: Environment & Dependency Setup

1.  **Initialize Virtual Environment**: Create a virtual environment using Python 3.12:
    ```bash
    python -m venv backend/.venv
    ```
2.  **Activate and Upgrade Pip**:
    ```bash
    backend/.venv/Scripts/python.exe -m pip install --upgrade pip setuptools
    ```
3.  **Install Deep Learning Modules (CPU wheel optimized)**:
    ```bash
    backend/.venv/Scripts/pip install torch==2.12.0 torchvision==0.27.0 --index-url https://download.pytorch.org/whl/cpu
    ```
4.  **Install Compatible MediaPipe & Protobuf**:
    ```bash
    backend/.venv/Scripts/pip install mediapipe==0.10.14 protobuf==4.25.9
    ```
5.  **Install Core Web Stack & Database Packages**:
    ```bash
    backend/.venv/Scripts/pip install fastapi>=0.115.0 uvicorn[standard]==0.24.0 pydantic==2.9.1 pydantic-settings==2.14.1 motor==3.7.1 pymongo[srv]==4.17.0 python-dotenv==1.0.0 gTTS==2.5.4 opencv-python scikit-learn pandas plotly streamlit==1.58.0 pytest
```

---

## Step 3: Global Configurations & Logger Setup

1.  **Create config/config.py**: Configure paths, directories, and variables.
2.  **Create config/logger.py**: Configure logs formatting.
3.  **Create ai_engine/utils/config.py**: Configure camera resolutions and detection thresholds.

---

## Step 4: Core Engine and Landmarking Modules

1.  **Create ai_engine/vision/camera_manager.py**: Handles webcam frames reading.
2.  **Create detectors** (`hand_detector.py`, `pose_detector.py`, `face_detector.py`): Extract MediaPipe joint coordinates.
3.  **Create ai_engine/landmark_processor/processor.py**: Implements the Exponential Moving Average (EMA) smoothing algorithm.
4.  **Create normalizers & feature builder modules**: Centering and scaling logic.
5.  **Create ai_engine/services/perception_service.py**: Aggregates the camera stream, landmark extraction, and coordinate smoothing into a single pipeline.

---

## Step 5: Gesture Classifier and PyTorch Models

1.  **Create ai_engine/gesture_recognition/models/word_model.py**: Defines sequential models (LSTM, BiLSTM, TCN, and Transformer).
2.  **Create ai_engine/gesture_recognition/models/alphabet_model.py**: Defines the fingerspelling MLP model.
3.  **Create predictors & services**: Handles model prediction sessions and custom data recording.

---

## Step 6: Database and Offline Storage

1.  **Create database/mongodb.py**: Singleton connection pool with timeout checks.
2.  **Create app/services/database_service.py**: Implements the offline local storage fallback mechanism.

---

## Step 7: Streamlit Frontend Pages

1.  **Create app/main.py**: Implements splash pages, authentication layouts, and global CSS.
2.  **Create pages**: Build the home dashboard, telemetry panel, cockpit panel, settings page, and other application pages.

---

## Step 8: FastAPI Backend Service

1.  **Create backend/app/main.py**: Starts the FastAPI web server.
2.  **Create backend/ws/telemetry_socket.py**: WebSocket endpoint for streaming coordinates.

---

## Step 9: Rebuild Validation Procedure

Run the validation suite to verify the application:

1.  **Verify import resolution**:
    ```bash
    backend/.venv/Scripts/python -c "import sys; sys.path.insert(0, '.'); from ai_engine.gesture_recognition.services.gesture_service import gesture_service; print('Imports verified!')"
    ```
2.  **Run Pytest tests**:
    ```bash
    backend/.venv/Scripts/pytest tests/
    ```
3.  **Launch the Streamlit app on port 8501**:
    ```bash
    backend/.venv/Scripts/python -m streamlit run app/main.py --server.port 8501
    ```
4.  **Open in browser**: Access `http://localhost:8501` to test the login flow and view the camera feed.
