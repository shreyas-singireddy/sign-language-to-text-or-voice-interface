import numpy as np
import mediapipe as mp
from typing import Tuple, List
from ai_engine.utils.logger import get_structured_logger
from ai_engine.utils.config import sys_config
from ai_engine.schemas.landmark_schema import Point3D, FaceTelemetryData

logger = get_structured_logger("vision.face")

class FaceDetector:
    def __init__(self):
        self.face_mesh = None
        if not hasattr(mp, "solutions"):
            logger.error("MediaPipe Solutions API is unavailable; face detection is disabled.")
            return

        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=sys_config.detectors.min_detection_confidence,
            min_tracking_confidence=sys_config.detectors.min_tracking_confidence
        )

    def process_frame(self, frame_rgb: np.ndarray) -> FaceTelemetryData:
        """
        Parses RGB frame and returns face telemetry structures.
        """
        if self.face_mesh is None:
            return FaceTelemetryData(present=False)

        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return FaceTelemetryData(present=False)

        face_landmarks = results.multi_face_landmarks[0]
        points = [
            Point3D(x=lm.x, y=lm.y, z=lm.z, visibility=1.0)
            for lm in face_landmarks.landmark
        ]

        # Calculate mouth openness: vertical lips gap vs lip width
        # Vertical center points: 13, 14. Horizontal corners: 78, 308
        gap = np.linalg.norm(np.array([points[13].x - points[14].x, points[13].y - points[14].y]))
        width = np.linalg.norm(np.array([points[78].x - points[308].x, points[78].y - points[308].y]))
        mouth_open = float(gap / (width + 1e-6))

        # Head Rotation estimation using key features
        # Yaw: horizontal eye balance relative to nose center (index 1 is nose tip, 33 left eye corner, 263 right eye)
        yaw = self._estimate_yaw(points[33], points[263], points[1])
        pitch = self._estimate_pitch(points[1], points[33], points[263])
        roll = self._estimate_roll(points[33], points[263])

        return FaceTelemetryData(
            present=True,
            landmarks=points,
            confidence=0.95,
            mouth_openness=round(mouth_open, 3),
            head_rotation_pitch=pitch,
            head_rotation_yaw=yaw,
            head_rotation_roll=roll,
            visibility=1.0
        )

    def _estimate_yaw(self, l_eye: Point3D, r_eye: Point3D, nose: Point3D) -> float:
        """Estimates horizontal yaw tilt."""
        left_dist = abs(nose.x - l_eye.x)
        right_dist = abs(r_eye.x - nose.x)
        diff = right_dist - left_dist
        # Scale to degrees
        return float(diff * 90.0)

    def _estimate_pitch(self, nose: Point3D, l_eye: Point3D, r_eye: Point3D) -> float:
        """Estimates vertical pitch tilt."""
        eyes_y = (l_eye.y + r_eye.y) / 2.0
        diff = nose.y - eyes_y
        # Scale to degrees
        return float((diff - 0.05) * 120.0)

    def _estimate_roll(self, l_eye: Point3D, r_eye: Point3D) -> float:
        """Estimates rotational roll tilt."""
        dx = r_eye.x - l_eye.x
        dy = r_eye.y - l_eye.y
        if abs(dx) < 1e-6:
            return 0.0
        return float(np.degrees(np.arctan2(dy, dx)))

    def close(self):
        """Release MediaPipe model."""
        if self.face_mesh is not None:
            self.face_mesh.close()
