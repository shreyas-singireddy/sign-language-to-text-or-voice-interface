# AI ENGINE BLUEPRINT - SignBridge AI Reconstruction Blueprint

This document details the functional specification of the SignBridge AI Engine pipeline.

---

## 1. Landmark Extraction & Smoothing Pipeline

```text
Webcam Frame (BGR)
       │
       ▼
[MediaPipe Holistic Ingest] ──► Extracts joints coordinate landmarks (x, y, z)
       │
       ▼
[EMA Smoothing Filter] ───────► Exponential Moving Average (EMA) capping jitter
       │
       ▼
[Landmark Normalizer] ────────► Scales and shifts landmarks around reference nodes
       │
       ▼
[Geometric Features Compiler] ► Compiles distances, angles, and velocity vectors
       │
       ▼
[PyTorch Classifiers Session] ► Predicts active gestures classes (Alphabet/Word)
```

---

## 2. MediaPipe Holistic Ingestion Configurations

*   **Tracking Modules**:
    *   *Hands Detector*: Evaluates 21 landmarks per hand ($X_{0..20}, Y_{0..20}, Z_{0..20}$). Key joints include `WRIST` (0), `THUMB_TIP` (4), `INDEX_FINGER_TIP` (8), `MIDDLE_FINGER_TIP` (12), `RING_FINGER_TIP` (16), and `PINKY_TIP` (20).
    *   *Pose Detector*: Focuses on upper body joints (`LEFT_SHOULDER` 11, `RIGHT_SHOULDER` 12, `LEFT_ELBOW` 13, `RIGHT_ELBOW` 14, `LEFT_WRIST` 15, `RIGHT_WRIST` 16).
    *   *Face Mesh*: Computes head rotation values (pitch, yaw, roll) and distance metrics (lips gap width).
*   **MediaPipe Parameters**:
    *   `static_image_mode = False` (runs continuous video tracking optimize loops).
    *   `max_num_hands = 2`.
    *   `min_detection_confidence = 0.5`.
    *   `min_tracking_confidence = 0.5`.

---

## 3. Coordinates Processing & Smoothing

### 3.1 Exponential Moving Average (EMA) Smoothing
To prevent video coordinate flutter (jitter), values are smoothed across consecutive frames using an EMA:
$$S_t = \alpha \cdot X_t + (1 - \alpha) \cdot S_{t-1}$$
*   **Smoothing factor ($\alpha$)**: Locked to `0.3`.
*   **Performance Metrics**: Variance drops from `0.0099` to `0.0015`, reducing coordination jitter by **84.75%**.

### 3.2 Landmarks Normalizer
*   *Translation Shift*: Shifts the coordinate axes relative to an anchor node (e.g. subtracting `WRIST` coordinates for hand landmarks, and `SHOULDER_CENTER` for body landmarks).
*   *Scale Normalization*: Divideds vectors by the bounding box size or hand length, ensuring distance changes are size-invariant.

---

## 4. PyTorch Neural Classifiers

### 4.1 Input & Sequence Padding
*   **Fingerspelling MLP**: Evaluates static vectors of size `126` (21 joints × 3 coords × 2 hands).
*   **Sequential Classifier**: Evaluates sequences of shape `(Batch, 30, Features)`. Pads shorter sequences to a length of 30 frames by repeating the last valid coordinate set.

### 4.2 Sequence Architectures (`word_model.py`)
1.  **LSTM / BiLSTM**: Models temporal dependencies over the 30-frame window.
2.  **Transformer**: Uses self-attention mechanisms to map dependencies across time steps.
3.  **TCN (Temporal Convolutional Networks)**: Uses dilated causal convolutions to process temporal sequences.

---

## 5. Decision & Post-Processing Logic

*   **Prediction Readiness Check**: Predictions are only generated if the frame meets the following thresholds:
    *   *Joint Visibility Score* $\ge$ 40%
    *   *Frame Quality Score* $\ge$ 35
    *   *Occlusion Percentage* $\le$ 40%
    *   *Tracking Stability* $\ge$ 30%
*   **Confidence Calculation**:
    *   Integrates raw classification probability, tracking stability, and joint visibility to calculate the final confidence score.
*   **Post-processing Smoothing**:
    *   Applies a temporal sliding window filter to stabilize the predictions and prevent rapid flickering of labels.

---

## 6. Translation & Audio Synthesis

*   **Rule-based Mappings Adapter**: Converts classified gesture tokens (e.g., `["HELLO", "THANK_YOU"]`) into grammatical sentences using custom dictionary mapping files in [translation/providers/rule_based.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/translation/providers/rule_based.py).
*   **TTS Synthesis Dispatcher**:
    *   *Online gTTS provider*: Synthesizes translated text to audio via Google Translate's TTS API, caching the resulting MP3 files.
    *   *Offline Browser provider*: Falls back to the browser's Web Speech Synthesis API if internet connectivity is lost.
