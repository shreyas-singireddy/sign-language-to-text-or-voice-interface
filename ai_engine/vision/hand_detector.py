import mediapipe as mp
import numpy as np

from ai_engine.schemas.landmark_schema import BoundingBox3D, HandTelemetryData, Point3D
from ai_engine.utils.config import sys_config
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("vision.hands")

# Diagnostic logging for MediaPipe initialization
try:
    logger.info(f"MediaPipe path: {getattr(mp, '__file__', 'unknown')}")
    logger.info(f"MediaPipe version: {getattr(mp, '__version__', 'unknown')}")
    logger.info(f"MediaPipe solutions available: {hasattr(mp, 'solutions')}")
except Exception as e:
    logger.error(f"MediaPipe diagnostic failed: {e}")


class HandDetector:
    def __init__(self):
        self.hands = None
        if not hasattr(mp, "solutions"):
            logger.error("MediaPipe Solutions API is unavailable; hand detection is disabled.")
            return

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=sys_config.detectors.min_detection_confidence,
            min_tracking_confidence=sys_config.detectors.min_tracking_confidence,
        )

    def process_frame(self, frame_rgb: np.ndarray) -> tuple[HandTelemetryData, HandTelemetryData]:
        """
        Parses RGB frame matrix and returns (left_hand, right_hand) telemetry records.
        """
        if self.hands is None:
            return HandTelemetryData(present=False), HandTelemetryData(present=False)

        results = self.hands.process(frame_rgb)

        # Initialize default mock instances
        left_hand = HandTelemetryData(present=False)
        right_hand = HandTelemetryData(present=False)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # MediaPipe classifies hands mirroring (Left vs Right)
                label = handedness.classification[0].label  # "Left" or "Right"
                score = float(handedness.classification[0].score)

                # Format landmarks list
                points = [Point3D(x=lm.x, y=lm.y, z=lm.z, visibility=1.0) for lm in hand_landmarks.landmark]

                # Compute center and bounding bounds
                center, bbox = self._calculate_bounding_geometry(points)

                hand_data = HandTelemetryData(
                    present=True,
                    landmarks=points,
                    confidence=score,
                    center=center,
                    bounding_box=bbox,
                )

                if label == "Right":
                    # Due to mirror flip, MP "Right" hand matches user's Right Hand
                    right_hand = hand_data
                else:
                    left_hand = hand_data

        return left_hand, right_hand

    def _calculate_bounding_geometry(self, points: list[Point3D]) -> tuple[Point3D, BoundingBox3D]:
        """
        Computes 3D bounding boundaries and center point coordinate.
        """
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]

        center = Point3D(x=float(np.mean(xs)), y=float(np.mean(ys)), z=float(np.mean(zs)))

        bbox = BoundingBox3D(
            min_point=Point3D(x=float(np.min(xs)), y=float(np.min(ys)), z=float(np.min(zs))),
            max_point=Point3D(x=float(np.max(xs)), y=float(np.max(ys)), z=float(np.max(zs))),
        )

        return center, bbox

    def close(self):
        """Release MediaPipe model."""
        if self.hands is not None:
            self.hands.close()
