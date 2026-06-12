import numpy as np

from ai_engine.landmark_extraction.extractor import landmark_extractor
from ai_engine.vision.hand_detector import HandDetector


class MockLandmark:
    def __init__(self, x: float, y: float, z: float, visibility: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

class MockLandmarkList:
    def __init__(self, count: int, has_visibility: bool = False):
        if has_visibility:
            self.landmark = [MockLandmark(0.1 * i, 0.2 * i, 0.3 * i, 0.9) for i in range(count)]
        else:
            self.landmark = [MockLandmark(0.1 * i, 0.2 * i, 0.3 * i) for i in range(count)]

class MockResults:
    def __init__(self, pose=None, face=None, left_hand=None, right_hand=None):
        self.pose_landmarks = pose
        self.face_landmarks = face
        self.left_hand_landmarks = left_hand
        self.right_hand_landmarks = right_hand

def test_hand_landmark_extraction_dimensions():
    # Verify shape of extracted landmarks (1662 coordinates)
    landmarks = landmark_extractor.extract_landmarks(None)
    assert isinstance(landmarks, np.ndarray)
    assert landmarks.shape == (1662,)

def test_hand_tracking_empty_default():
    landmarks = landmark_extractor.extract_landmarks(None)
    assert np.all(landmarks == 0)

def test_hand_landmark_extraction_with_data():
    pose = MockLandmarkList(33, has_visibility=True)
    face = MockLandmarkList(468)
    lh = MockLandmarkList(21)
    rh = MockLandmarkList(21)

    results = MockResults(pose=pose, face=face, left_hand=lh, right_hand=rh)

    landmarks = landmark_extractor.extract_landmarks(results)
    assert landmarks.shape == (1662,)
    assert landmarks[0] == 0.0 # lm.x of first pose
    assert landmarks[132] == 0.0 # lm.x of first face

    assert landmark_extractor.has_hands_detected(results) is True
    assert landmark_extractor.has_hands_detected(None) is False

def test_hand_detector_empty_frame():
    detector = HandDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    lh, rh = detector.process_frame(frame)
    assert lh.present is False
    assert rh.present is False
    detector.close()
