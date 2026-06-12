# Spec-Kit: Hand Tracking Subsystem

## 1. Purpose
The Hand Tracking Subsystem processes input video frames to identify, extract, and track the spatial positions (21 landmarks) of the left and right hands in real time.

## 2. Requirements
- **REQ-HT-001**: Concurrent tracking of two hands (left and right) at a minimum of 30 frames per second.
- **REQ-HT-002**: Extraction of 21 3D landmarks (x, y, z coordinates) per hand.
- **REQ-HT-003**: Graceful degradation (returns default coordinates) when hands are not visible in the frame.

## 3. Architecture
- **Inference Engine**: MediaPipe Hands framework running locally.
- **Input**: NumPy image matrices (RGB/BGR, 640x480 resolution).
- **Output**: JSON or dictionary containing normalized coordinates.

## 4. Acceptance Criteria
- Tracking must report hand presence status accurately in the metadata.
- Processing latency for landmark extraction must be under 30ms per frame on typical CPU environments.

## 5. Performance Targets
- FPS: >= 30 FPS.
- Coordinate error margin: <= 0.05 absolute unit deviation from ground truth.

## 6. Security Considerations
- Frame processing is done entirely client-side/in-memory; video frames must never be persisted or sent over network sockets to protect user privacy.

## 7. Risks
- Motion blur or dim lighting can reduce tracking confidence. System must dynamically calculate a brightness score to warn users of poor lighting.

## 8. Test Cases
- **Test-HT-1**: Verify landmark format of shape `(1662,)` when input is empty or None.
- **Test-HT-2**: Check concurrent dual-hand tracking on static test images.

## 9. Verification Procedures
1. Run pytest suite testing hand extraction stubs:
   ```bash
   pytest tests/test_scaffolding.py -k "test_landmark_extractor"
   ```
2. Verify visual output overlays via the Streamlit Developer Console webcam check page.
