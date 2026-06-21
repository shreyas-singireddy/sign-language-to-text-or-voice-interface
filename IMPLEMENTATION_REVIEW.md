# IMPLEMENTATION REVIEW - SignBridge AI Human Perception System

This document provides a detailed review of the implementation details, algorithms, and inputs/outputs for each component in the system.

---

## 1. Face Mesh & Tracking

*   **Role**: Detects and tracks 3D facial coordinates to estimate head pose, mouth movement, and expressions.
*   **Responsible File**: [face_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/face_detector.py)
*   **Algorithms**: MediaPipe `FaceMesh` (residual neural network framework mapping coordinates on frame).
*   **Data Ingest**: RGB Frame matrix `np.ndarray` shape `(height, width, 3)`.
*   **Data Output**: `FaceTelemetryData` containing 468 `Point3D` coordinates, head rotation pitch/yaw/roll floats, mouth openness float, and visibility float.
*   **Internal Mechanics**:
    *   Estimates mouth openness by calculating the ratio of the vertical lip gap (between landmarks 13 and 14) to the horizontal lip width (between landmarks 78 and 308).
*   **Limitations**: High latency under multi-face configurations, and fails to track facial landmarks under side-profile occlusions.

---

## 2. Head Pose & Eye Tracking

*   **Role**: Estimates head rotation angles (pitch, yaw, roll) and eye coordinates for gaze tracking.
*   **Responsible File**: [face_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/face_detector.py)
*   **Algorithms**: Heuristic distance differentials mapping coordinates:
    *   *Yaw*: Distance differential between the nose tip (index 1) and the left/right eye corners (indices 33 and 263).
    *   *Pitch*: Distance differential between the nose tip and the midpoint between the eyes.
    *   *Roll*: The arctangent of the angle between the left and right eye corners.
*   **Data Ingest**: 468 Face `Point3D` array.
*   **Data Output**: Rotation floats (pitch, yaw, roll) scaled in degrees.
*   **Limitations**: Calculations are heuristic and susceptible to positioning errors. It does not use PnP (Perspective-n-Point) solvers.

---

## 3. Hand & Finger Tracking

*   **Role**: Tracks 21 landmarks per hand, computes bounding boxes, and calculates fingers curl status.
*   **Responsible Files**:
    *   [hand_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/hand_detector.py)
    *   [landmark_features.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/features/landmark_features.py)
*   **Algorithms**: MediaPipe `Hands` tracking model.
*   **Data Ingest**: RGB Frame matrix `np.ndarray`.
*   **Data Output**: `HandTelemetryData` containing 21 `Point3D` coordinates, classification confidence float, center `Point3D`, and `BoundingBox3D`.
*   **Finger tracking logic**:
    *   Computes finger curls as the ratio of the tip-to-wrist distance to the MCP-to-wrist distance.
    *   MCP-PIP-DIP joint angles are calculated using dot-product cosine vector rules.
*   **Limitations**: Hand coordinates overlap with face mesh coordinates in the raw flat array. The system loses tracking during rapid hand movement (motion blur) or hand-on-hand occlusion.

---

## 4. Body / Pose Tracking

*   **Role**: Tracks 33 body skeletal landmarks, computing elbow/shoulder angles and torso rotation.
*   **Responsible File**: [pose_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/pose_detector.py)
*   **Algorithms**: MediaPipe `Pose` tracking solution.
*   **Data Ingest**: RGB Frame matrix `np.ndarray`.
*   **Data Output**: `PoseTelemetryData` containing 33 `Point3D` landmarks, left/right arm angles, shoulder angles, and torso rotation.
*   **Joint angle calculation**: Joint angles are calculated using the dot-product cosine vector rule at the joint vertex:
    $$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right)$$
*   **Limitations**: High latency. Does not support tracking multiple people simultaneously.

---

## 5. Telemetry Ingestion Engine

*   **Role**: Orchestrates frame processing, normalizes coordinates, applies EMA smoothing, and calculates performance metrics.
*   **Responsible File**: [perception_service.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/services/perception_service.py)
*   **Algorithms**:
    *   *Smoothing*: Exponential Moving Average (EMA) with $\alpha=0.3$.
    *   *Quality Check*: Brightness mean analysis and Laplacian variance calculations to estimate frame blur.
*   **Data Ingest**: BGR Camera Frame `np.ndarray`.
*   **Data Output**: Unified `TelemetryResponse` object containing smoothed landmarks, motion, stability, visibility, occlusion, and performance metrics.
*   **Limitations**: Hardcoded offset mapping bugs (left hand at 1404, right hand at 1467) corrupt the flat coordinates array.

---

## 6. Gesture Classification & Sequence Models

*   **Role**: Classifies fingerspelling characters and temporal word gestures.
*   **Responsible Files**:
    *   [predictor.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/inference/predictor.py)
    *   [word_model.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/models/word_model.py)
*   **Algorithms**:
    *   *Alphabet Model*: Multi-Layer Perceptron (MLP) for static coordinates classification.
    *   *Word Model*: Recurrent neural networks (LSTM, BiLSTM, TCN Dilated Causal Convolution, and Transformer with Self-Attention).
*   **Data Ingest**: Engineered feature vector shape `(52,)` or sequence buffer `(30, 1662)`.
*   **Data Output**: Classification label token string, probability confidence score, and candidate lists.
*   **Limitations**: Overlapping array indices feed corrupted landmarks to the predictors, reducing classification accuracy.

---

## 7. Model Training System

*   **Role**: Loads local datasets, splits data, trains gesture classifiers, and saves checkpoints to the model registry.
*   **Responsible Files**:
    *   [trainer.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/training/trainer.py)
    *   [dataset_manager.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/dataset/dataset_manager.py)
*   **Algorithms**: Backpropagation using PyTorch, Adam optimizer, cross-entropy loss, and learning rate scheduling.
*   **Data Ingest**: Directory containing raw `.npy` sequence files.
*   **Data Output**: Versioned model weight checkpoints (`.pt` files) and registration metadata JSONs.
*   **Limitations**: Incomplete training data falls back to synthetic datasets, which do not represent real-world gestures.
