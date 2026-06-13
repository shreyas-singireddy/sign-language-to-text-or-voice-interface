from ai_engine.utils.cv2_guard import cv2
import mediapipe as mp
import numpy as np

from ai_engine.schemas.landmark_schema import FaceTelemetryData, Point3D
from ai_engine.utils.config import sys_config
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("vision.face")


class FaceDetector:
    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=sys_config.detectors.min_detection_confidence,
            min_tracking_confidence=sys_config.detectors.min_tracking_confidence,
        )

    def process_frame(self, frame_rgb: np.ndarray) -> FaceTelemetryData:
        """
        Parses RGB frame and returns face telemetry structures.
        """
        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:
            return FaceTelemetryData(present=False)

        face_landmarks = results.multi_face_landmarks[0]
        points = [Point3D(x=lm.x, y=lm.y, z=lm.z, visibility=1.0) for lm in face_landmarks.landmark]

        # Calculate mouth openness: vertical lips gap vs lip width
        # Vertical center points: 13, 14. Horizontal corners: 78, 308
        gap = np.linalg.norm(np.array([points[13].x - points[14].x, points[13].y - points[14].y]))
        width = np.linalg.norm(np.array([points[78].x - points[308].x, points[78].y - points[308].y]))
        mouth_open = float(gap / (width + 1e-6))

        # Head Rotation estimation using Perspective-n-Point (PnP)
        img_h, img_w, _ = frame_rgb.shape

        # Select 2D image coordinates from MediaPipe FaceMesh
        # indices: 1 = nose tip, 152 = chin, 33 = left eye outer corner, 263 = right eye outer corner, 61 = left mouth corner, 291 = right mouth corner
        image_points = np.array(
            [
                [points[1].x * img_w, points[1].y * img_h],  # Nose tip
                [points[152].x * img_w, points[152].y * img_h],  # Chin
                [points[33].x * img_w, points[33].y * img_h],  # Left eye corner
                [points[263].x * img_w, points[263].y * img_h],  # Right eye corner
                [points[61].x * img_w, points[61].y * img_h],  # Left mouth corner
                [points[291].x * img_w, points[291].y * img_h],  # Right mouth corner
            ],
            dtype="double",
        )

        # 3D model points of a standard head mesh
        model_points = np.array(
            [
                (0.0, 0.0, 0.0),  # Nose tip
                (0.0, -330.0, -65.0),  # Chin
                (-225.0, 170.0, -135.0),  # Left eye corner
                (225.0, 170.0, -135.0),  # Right eye corner
                (-150.0, -150.0, -125.0),  # Left mouth corner
                (150.0, -150.0, -125.0),  # Right mouth corner
            ],
            dtype="double",
        )

        focal_length = img_w
        center = (img_w / 2.0, img_h / 2.0)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
            dtype="double",
        )
        dist_coeffs = np.zeros((4, 1))

        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        pitch, yaw, roll = 0.0, 0.0, 0.0
        if success:
            rmat, _ = cv2.Rodrigues(rotation_vector)
            # Compute Euler angles from rotation matrix
            sy = np.sqrt(rmat[0, 0] * rmat[0, 0] + rmat[1, 0] * rmat[1, 0])
            singular = sy < 1e-6
            if not singular:
                pitch = np.arctan2(rmat[2, 1], rmat[2, 2])
                yaw = np.arctan2(-rmat[2, 0], sy)
                roll = np.arctan2(rmat[1, 0], rmat[0, 0])
            else:
                pitch = np.arctan2(-rmat[1, 2], rmat[1, 1])
                yaw = np.arctan2(-rmat[2, 0], sy)
                roll = 0.0

            pitch = round(float(np.degrees(pitch)), 2)
            yaw = round(float(np.degrees(yaw)), 2)
            roll = round(float(np.degrees(roll)), 2)

        return FaceTelemetryData(
            present=True,
            landmarks=points,
            confidence=0.95,
            mouth_openness=round(mouth_open, 3),
            head_rotation_pitch=pitch,
            head_rotation_yaw=yaw,
            head_rotation_roll=roll,
            visibility=1.0,
        )

    def close(self):
        """Release MediaPipe model."""
        self.face_mesh.close()
