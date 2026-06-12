import numpy as np

from ai_engine.processing.landmark_normalizer import landmark_normalizer
from ai_engine.schemas.landmark_schema import (
    FaceTelemetryData,
    FrameLandmarkData,
    HandTelemetryData,
    PoseTelemetryData,
)
from ai_engine.vision.pose_detector import PoseDetector


def test_body_tracking_normalization():
    # Construct empty landmark frame
    frame = FrameLandmarkData(
        timestamp=100.0,
        left_hand=HandTelemetryData(present=False),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=False),
        face=FaceTelemetryData(present=False),
    )

    norm = landmark_normalizer.normalize_frame(frame)
    assert norm.pose.present is False


def test_pose_detector_empty_frame():
    detector = PoseDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    pose_data = detector.process_frame(frame)
    assert pose_data.present is False
    detector.pose.close()
