# COMPUTER VISION PIPELINE - SignBridge AI Reconstruction Blueprint

This document details the configuration parameters, camera frame capture loops, and hardware requirements of the Computer Vision pipeline in SignBridge AI.

---

## 1. MediaPipe Detector Configurations

The pipeline initializes distinct MediaPipe tracking estimators configured as follows:

### 1.1 Hand Tracking Estimator
*   `static_image_mode = False` (processes frames as a continuous video sequence).
*   `max_num_hands = 2` (supports dual-handed gestures).
*   `min_detection_confidence = 0.5` (initial detector threshold).
*   `min_tracking_confidence = 0.5` (subsequent coordinate tracking threshold).

### 1.2 Pose skeletal Estimator
*   `static_image_mode = False`.
*   `model_complexity = 1` (balances tracking accuracy with real-time performance).
*   `smooth_landmarks = True` (applies MediaPipe's internal coordinate smoothing).
*   `min_detection_confidence = 0.5`.
*   `min_tracking_confidence = 0.5`.

### 1.3 Face mesh Estimator
*   `static_image_mode = False`.
*   `max_num_faces = 1`.
*   `refine_landmarks = True` (refines coordinates for lips, eyes, and iris detail).
*   `min_detection_confidence = 0.5`.
*   `min_tracking_confidence = 0.5`.

---

## 2. Ingest & Camera Configurations

Default capture properties configured in `CameraSettings`:
*   **Webcam Device Index**: `0` (typically refers to the system's primary integrated camera).
*   **Frame Resolution**: `640x480` pixels (standard default selected to optimize processing speed).
*   **Frame Rate Limit**: `30 FPS` cap (avoids unnecessary CPU overhead from processing redundant frames).

```python
# Real-time capture loop pattern
read_success, frame, latency = perception_service.camera.read_frame()
if read_success:
    telemetry_data = perception_service.process_perception_frame(frame, latency)
```

---

## 3. Hardware Requirements & Performance Variance

Computer vision execution speed depends heavily on system hardware:

*   **CPU Overhead**: MediaPipe runs coordinates estimations in real-time. On systems with older dual-core CPUs, running all three detectors (hands, pose, face) simultaneously can cause frame drops and lower the frame rate to <15 FPS.
*   **RAM Allocation**: Real-time video buffering and memory allocations require a minimum of **8GB RAM** to prevent memory thrashing.
*   **GPU Acceleration**: On devices configured with OpenCL or CUDA, model inference runs significantly faster, maintaining stable performance above 30 FPS.
*   **Lighting and Camera Quality**:
    *   *Low light environments* can introduce noise to camera frames, causing the detector to lose track of hand coordinates and trigger the fallback state: `WAITING_FOR_CLEAR_GESTURE`.
    *   *Auto-focus delays* can cause temporary motion blur, reducing the frame quality score and blocking prediction engines until coordinates stabilize.
