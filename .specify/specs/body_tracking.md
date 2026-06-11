# Spec-Kit: Body Tracking Subsystem

## 1. Overview & Objectives
The Body Tracking Subsystem extracts torso, shoulder, and arm landmarks to evaluate pose dynamics and support gesture interpretation that incorporates body movement.

## 2. Requirements & Traceability
- **REQ-BT-001**: Must track upper body/torso skeleton structures utilizing MediaPipe Pose.
- **REQ-BT-002**: Must return elbow, wrist, and shoulder coordinates for translation normalization.

## 3. Interface Definitions
```python
class BodyTracker:
    def process_frame(self, frame: np.ndarray) -> dict:
        """Processes video frame to extract pose landmarks.
        Returns:
            dict containing wrist, elbow, and shoulder coordinates.
        """
        pass
```

## 4. Verification Plan
- **Test-BT-001**: Verified via `tests/test_body_tracking.py` to validate coordinate formatting and model load accuracy.
