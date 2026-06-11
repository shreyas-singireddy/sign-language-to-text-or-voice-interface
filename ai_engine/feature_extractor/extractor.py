import numpy as np

from config.logger import setup_logger

logger = setup_logger("ai_engine.feature_extractor")


class FeatureExtractor:
    def __init__(self):
        self.prev_landmarks = None
        self.prev_velocities = None

    def calculate_distances(self, landmarks: np.ndarray) -> dict:
        """
        Computes Euclidean distance between keypoints (e.g. thumb tip to index tip).
        - Left hand index tip is at 1536 + (8 * 3) = 1560
        - Left hand thumb tip is at 1536 + (4 * 3) = 1548
        - Right hand index tip is at 1599 + (8 * 3) = 1623
        - Right hand thumb tip is at 1599 + (4 * 3) = 1611
        """
        distances = {}

        lh_thumb = landmarks[1548:1551]
        lh_index = landmarks[1560:1563]
        rh_thumb = landmarks[1611:1614]
        rh_index = landmarks[1623:1626]

        # Left hand pinch distance
        if np.any(lh_thumb != 0) and np.any(lh_index != 0):
            distances["lh_thumb_index"] = float(np.linalg.norm(lh_thumb - lh_index))
        else:
            distances["lh_thumb_index"] = 0.0

        # Right hand pinch distance
        if np.any(rh_thumb != 0) and np.any(rh_index != 0):
            distances["rh_thumb_index"] = float(np.linalg.norm(rh_thumb - rh_index))
        else:
            distances["rh_thumb_index"] = 0.0

        # Hand to Hand distance (wrists center)
        lh_wrist = landmarks[1536:1539]
        rh_wrist = landmarks[1599:1602]
        if np.any(lh_wrist != 0) and np.any(rh_wrist != 0):
            distances["hand_to_hand"] = float(np.linalg.norm(lh_wrist - rh_wrist))
        else:
            distances["hand_to_hand"] = 0.0

        return distances

    def calculate_angles(self, landmarks: np.ndarray) -> dict:
        """
        Computes joint angles using dot product vector rules.
        e.g., Elbow angle using Shoulder, Elbow, and Wrist.
        - Pose landmarks: Left Shoulder (11 * 4 = 44), Left Elbow (13 * 4 = 52), Left Wrist (15 * 4 = 60)
        """
        angles = {}

        # Extract pose segments
        l_shoulder = landmarks[44:47]
        l_elbow = landmarks[52:55]
        l_wrist = landmarks[60:63]

        if np.any(l_shoulder != 0) and np.any(l_elbow != 0) and np.any(l_wrist != 0):
            # Vector 1: Shoulder to Elbow
            v1 = l_shoulder - l_elbow
            # Vector 2: Wrist to Elbow
            v2 = l_wrist - l_elbow

            # Angle computation
            cos_theta = np.dot(v1, v2) / (
                np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6
            )
            angle = np.arccos(np.clip(cos_theta, -1.0, 1.0))
            angles["left_elbow_angle"] = float(np.degrees(angle))
        else:
            angles["left_elbow_angle"] = 180.0  # Standard open arm default

        return angles

    def calculate_velocities_and_accelerations(self, landmarks: np.ndarray) -> tuple:
        """
        Computes spatial displacement (velocity) and change of displacement (acceleration).
        Returns:
            velocities (np.ndarray): flat velocity vector shape (1662,)
            accelerations (np.ndarray): flat acceleration vector shape (1662,)
        """
        velocities = np.zeros(1662)
        accelerations = np.zeros(1662)

        if self.prev_landmarks is not None:
            # First-order difference: v = x_t - x_{t-1}
            velocities = landmarks - self.prev_landmarks

            if self.prev_velocities is not None:
                # Second-order difference: a = v_t - v_{t-1}
                accelerations = velocities - self.prev_velocities

            self.prev_velocities = velocities.copy()

        self.prev_landmarks = landmarks.copy()
        return velocities, accelerations

    def extract_all(self, landmarks: np.ndarray) -> dict:
        """
        Assembles all computed features.
        """
        distances = self.calculate_distances(landmarks)
        angles = self.calculate_angles(landmarks)
        velocities, accelerations = self.calculate_velocities_and_accelerations(
            landmarks
        )

        return {
            "distances": distances,
            "angles": angles,
            "mean_velocity": float(np.mean(np.abs(velocities))),
            "mean_acceleration": float(np.mean(np.abs(accelerations))),
            "velocity_vector": velocities.tolist(),
            "acceleration_vector": accelerations.tolist(),
        }


feature_extractor = FeatureExtractor()
