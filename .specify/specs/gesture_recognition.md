# Spec-Kit: Gesture Recognition Engine

## 1. Overview & Objectives
The Gesture Recognition Engine processes extracted sequences of hand/body coordinates and feeds them into a trained sequence neural network (PyTorch) to classify the sequence as a specific sign gesture (e.g. "HELLO", "YES", "NO", "PLEASE").

## 2. Requirements & Traceability
- **REQ-GR-001**: Must classify dynamic sequences with confidence scores.
- **REQ-GR-002**: Must handle frame windowing (temporal sequences of 30 frames) for classification.
- **REQ-GR-003**: Must map recognized indexes to one of the supported gesture keys: HELLO, THANKS, YES, NO, PLEASE, SORRY, HELP, GOOD MORNING, GOOD NIGHT.

## 3. Interface Definitions
```python
class GesturePredictor:
    def predict(self, landmarks_sequence: np.ndarray) -> tuple[str, float]:
        """Classifies a sequence of landmark frames.
        Returns:
            Tuple of (gesture_label, confidence_score).
        """
        pass
```

## 4. Verification Plan
- **Test-GR-001**: Tested in `tests/test_gesture_recognition.py` checking prediction output given standard numpy array shapes.
