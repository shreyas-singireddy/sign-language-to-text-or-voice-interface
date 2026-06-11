# GESTURE ENGINE REVIEW - SignBridge AI Human Perception System

This document reviews the classification algorithms, model structures, confidence calculations, and expected accuracy boundaries of the gesture recognition engine.

---

## 1. Classification Architectures

The system uses two different classification approaches depending on the type of gesture:

1.  **Fingerspelling (Static Gestures)**:
    *   *Model*: Multi-Layer Perceptron (MLP) defined in [alphabet_model.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/models/alphabet_model.py).
    *   *Classification*: Classifies single frames into one of 36 categories (A-Z, 0-9).
2.  **Sequential Gestures (Temporal Words)**:
    *   *Model*: Supports multiple sequential models defined in [word_model.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/models/word_model.py) (LSTM, BiLSTM, TCN, or Transformer).
    *   *Classification*: Classifies sequences of 30 frames into one of 10 word categories (such as `HELLO`, `THANK_YOU`, `HELP`).

---

## 2. Detection Logic & Sequence Processing

1.  **Ingestion Buffer**: Maintains a sliding window of the last 30 frames coordinates:
    ```python
    st.session_state["sequence_buffer"].append(flat_lms)
    ```
2.  **Readiness Check**: Passes the frame through quality filters (minimum visibility, quality, occlusion, and stability scores) in [predictor.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/inference/predictor.py#L98-L113).
3.  **Forward Pass**: Pads shorter sequences to a length of 30 frames and runs inference using PyTorch or ONNX runtimes.
4.  **Post-Processing & Smoothing**: Confirms the prediction by applying a temporal window filter to stabilize the outputs and prevent rapid flickering:
    ```python
    smoothed_label = post_processor.smooth_predictions(prediction_label)
    ```

---

## 3. Confidence Calculation

The system calculates the final confidence score by combining the classification probability with real-time tracking metrics:

```python
smooth_confidence = confidence_engine.calculate_confidence(
    raw_probability, prediction_label, stability_score, visibility_score
)
```

*   **Raw Probability**: The softmax output score from the model ($0.0 \dots 1.0$).
*   **Stability Coefficient**: Penalizes the confidence score if coordinate jitter is high.
*   **Visibility Coefficient**: Reduces confidence if key joints are occluded.

---

## 4. Current Limitations & Expected Accuracy

*   **Coordinates Index Mapping Bug (Critical)**:
    *   Because the left hand (`1404`) and right hand (`1467`) offsets overlap with the face mesh array indices, the models are trained on corrupted face coordinates when hands are not present.
    *   This limits the classification accuracy of temporal word models to **~60-70%** in real-world scenarios.
*   **Sequence Length Constraints**:
    *   The model assumes a fixed sequence length of 30 frames.
    *   If a user performs a gesture too quickly or too slowly, the padding/truncation step can distort the temporal sequence, reducing classification accuracy.
*   **Camera Frame Drops**:
    *   If the camera frame rate drops below 20 FPS, the temporal sequence is warped, causing prediction errors.
