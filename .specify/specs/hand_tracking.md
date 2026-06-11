# Spec-Kit: Hand Tracking Subsystem

## 1. Overview & Objectives
The Hand Tracking Subsystem captures real-time video frames from the camera, runs the MediaPipe hand detection solution, and extracts spatial coordinate points (X, Y, Z, and visibility metrics) for 21 structural landmarks per hand.

## 2. Requirements & Traceability
- **REQ-HT-001**: Must track left and right hands concurrently up to 30 frames per second.
- **REQ-HT-002**: Must return exactly 21 coordinate points per tracked hand.
- **REQ-HT-003**: If no hand is present, landmark coordinates must fallback to standard zeroes rather than throwing exceptions or interrupting the pipeline.

## 3. Interface Definitions
```python
class HandTracker:
    def process_frame(self, frame: np.ndarray) -> dict:
        """Processes video frame to find hand landmarks.
        Returns:
            dict containing lists of landmarks (x, y, z) for left and right hands.
        """
        pass
```

## 4. Verification Plan
- **Test-HT-001**: Verified via `tests/test_hand_tracking.py` (which tests mock image inputs and checks return dictionary structure).
