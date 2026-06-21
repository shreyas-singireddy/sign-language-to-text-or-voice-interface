import numpy as np

from app.utils.mediapipe_model import MEDIA_AVAILABLE, SignLanguageModel


def test_model_initialization():
    model = SignLanguageModel()
    assert model.confidence == 0.0
    if MEDIA_AVAILABLE:
        assert model.hands is not None


def test_predict_no_hands():
    model = SignLanguageModel()
    # Create a blank black image
    blank_image = np.zeros((480, 640, 3), dtype=np.uint8)

    prediction = model.predict(blank_image)
    assert prediction == "NO_HANDS"
    assert model.confidence == 0.0


def test_normalization():
    model = SignLanguageModel()

    # Mock landmarks
    class MockLandmark:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    mock_lms = [MockLandmark(0.1, 0.1, 0.0), MockLandmark(0.5, 0.5, 0.0), MockLandmark(0.9, 0.9, 0.0)]

    normalized = model.normalize_landmarks(mock_lms)

    # x_min=0.1, x_max=0.9, width=0.8
    # y_min=0.1, y_max=0.9, height=0.8
    # First normalized: (0.1-0.1)/0.8 = 0.0
    assert normalized[0] == 0.0
    assert normalized[1] == 0.0

    # Second normalized: (0.5-0.1)/0.8 = 0.5
    assert normalized[3] == 0.5
    assert normalized[4] == 0.5
