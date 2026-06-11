# ACCURACY BOTTLENECK REPORT - SignBridge AI Human Perception System

This report ranks and explains the primary bottlenecks that limit the accuracy of the SignBridge AI tracking and prediction pipelines.

---

## 1. Rank: 1 (CRITICAL SEVERITY) — Coordinates Index Mapping Bug

*   **Problem**: In `_flatten_landmarks` (and its corresponding unpacker/updater), the left hand starts at index `1404` and the right hand at index `1467`.
*   **Root Cause**:
    *   The face mesh has 468 landmarks × 3 coordinates (`1404` values), which occupy indices `132` to `1535` in the flat array.
    *   As a result, the hand coordinates overlap with and overwrite face landmarks starting at index `1404` (face landmark `424`).
    *   If no hands are detected, the indices `1404` to `1530` contain lingering face coordinates, which are incorrectly processed as hand coordinates by the feature extractor.
*   **Impact**:
    *   The system processes facial movements as hand gestures when hands are not present.
    *   This limits the classification accuracy of temporal word models to **~60-70%**.

---

## 2. Rank: 2 (HIGH SEVERITY) — Synthetic Dataset Fallback

*   **Problem**: When no recorded gesture sequences are found on disk, the system falls back to generating synthetic training data.
*   **Root Cause**: The synthetic generator uses simple sine wave curves to simulate hand movements.
*   **Impact**:
    *   Synthetic datasets do not represent the variance and complexity of real-world sign language gestures.
    *   Models trained on synthetic data fail to generalize when evaluated on real-world inputs.

---

## 3. Rank: 3 (MEDIUM SEVERITY) — Lighting & Exposure Sensitivity

*   **Problem**: Low-light or back-lit environments cause coordinate jitter and tracking drops.
*   **Root Cause**:
    *   In low-light conditions, camera noise and motion blur increase.
    *   This reduces MediaPipe's detection confidence below the `0.5` threshold, causing the tracker to lose alignment.
*   **Impact**: The system falls back to the `WAITING_FOR_CLEAR_GESTURE` state, blocking predictions.

---

## 4. Rank: 4 (MEDIUM SEVERITY) — Fixed Sequence Length Constraints

*   **Problem**: The model assumes a fixed sequence length of 30 frames.
*   **Root Cause**:
    *   If a user performs a gesture too quickly or too slowly, the padding/truncation step can distort the temporal sequence.
*   **Impact**: This structural warping reduces the classification accuracy of sequential models.

---

## 5. Rank: 5 (LOW SEVERITY) — Camera Frame Rate Drops

*   **Problem**: Frame rate drops below 20 FPS cause coordinate drift and classification errors.
*   **Root Cause**: CPU overhead from running multiple MediaPipe estimators simultaneously can cause the frame rate to drop on older hardware.
*   **Impact**: The model receives fewer frames per gesture, warping the temporal sequence and reducing accuracy.
