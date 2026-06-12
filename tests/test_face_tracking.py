import numpy as np

from ai_engine.landmark_extraction.extractor import landmark_extractor
from ai_engine.vision.face_detector import FaceDetector


def test_face_landmarks_placeholder_fallback():
    # Face mesh index maps to specific landmarks. Check default fallback structure.
    landmarks = landmark_extractor.extract_landmarks(None)
    assert len(landmarks) == 1662
    # Verify that face landmark fields (which are a subslice of the 1662 vector) default to 0
    face_slice = landmarks[468:936]
    assert np.all(face_slice == 0)


def test_face_detector_empty_frame():
    detector = FaceDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    face_data = detector.process_frame(frame)
    assert face_data.present is False
    detector.face_mesh.close()
