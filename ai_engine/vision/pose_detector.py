import numpy as np
import mediapipe as mp
from typing import Tuple, List
from ai_engine.utils.logger import get_structured_logger
from ai_engine.utils.config import sys_config
from ai_engine.schemas.landmark_schema import Point3D, PoseTelemetryData

logger = get_structured_logger("vision.pose")

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=sys_config.detectors.min_detection_confidence,
            min_tracking_confidence=sys_config.detectors.min_tracking_confidence
        )

    def process_frame(self, frame_rgb: np.ndarray) -> PoseTelemetryData:
        """
        Parses RGB frame and returns pose telemetry structures.
        """
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return PoseTelemetryData(present=False)

        # Convert all landmarks
        points = [
            Point3D(x=lm.x, y=lm.y, z=lm.z, visibility=float(lm.visibility))
            for lm in results.pose_landmarks.landmark
        ]

        # Calculate joint telemetry angles
        left_arm = self._calculate_angle(points[11], points[13], points[15])   # Shoulder-Elbow-Wrist (L)
        right_arm = self._calculate_angle(points[12], points[14], points[16])  # Shoulder-Elbow-Wrist (R)
        shoulder_ang = self._calculate_angle(points[13], points[11], points[12]) # Elbow-Shoulder-Shoulder
        
        # Torso rotation yaw estimation (Left shoulder vs Right shoulder z depth differential)
        torso_rot = self._calculate_torso_rotation(points[11], points[12])

        return PoseTelemetryData(
            present=True,
            landmarks=points,
            confidence=0.92, # Estimated tracking coefficient
            left_arm_angle=left_arm,
            right_arm_angle=right_arm,
            shoulder_angle=shoulder_ang,
            torso_rotation=torso_rot
        )

    def _calculate_angle(self, p1: Point3D, p2: Point3D, p3: Point3D) -> float:
        """
        Computes 3D joint vector angle with cosine dot product rules.
        p2 is the joint vertex.
        """
        # Vectors
        v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom < 1e-6:
            return 180.0
            
        cos_theta = np.dot(v1, v2) / denom
        angle = np.arccos(np.clip(cos_theta, -1.0, 1.0))
        return float(np.degrees(angle))

    def _calculate_torso_rotation(self, l_sh: Point3D, r_sh: Point3D) -> float:
        """
        Estimates torso rotation yaw from z depth differences.
        """
        dx = r_sh.x - l_sh.x
        dz = r_sh.z - l_sh.z
        if abs(dx) < 1e-6:
            return 0.0
        angle = np.arctan2(dz, dx)
        return float(np.degrees(angle))

    def close(self):
        """Release MediaPipe model."""
        self.pose.close()
