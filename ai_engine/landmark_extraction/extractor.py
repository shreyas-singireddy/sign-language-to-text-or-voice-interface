import numpy as np
from config.logger import setup_logger

logger = setup_logger("ai_engine.landmark_extraction")

class LandmarkExtractor:
    """
    Extracts pose, face, left hand, and right hand landmarks from MediaPipe results
    and packs them into a single flattened feature vector of size 1662.
    
    - Pose: 33 landmarks * 4 features (x, y, z, visibility) = 132
    - Face: 468 landmarks * 3 features (x, y, z) = 1404
    - Left Hand: 21 landmarks * 3 features (x, y, z) = 63
    - Right Hand: 21 landmarks * 3 features (x, y, z) = 63
    - Total: 132 + 1404 + 63 + 63 = 1662 features.
    """
    
    def extract_landmarks(self, results) -> np.ndarray:
        """
        Processes raw MediaPipe results and outputs a single flat numpy array of shape (1662,).
        If results is None or elements are missing, they are filled with zeros.
        """
        if results is None:
            return np.zeros(1662)

        # Pose (33 landmarks * 4 coordinates = 132)
        if results.pose_landmarks:
            pose = np.array([
                [lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark
            ]).flatten()
        else:
            pose = np.zeros(33 * 4)

        # Face (468 landmarks * 3 coordinates = 1404)
        if results.face_landmarks:
            face = np.array([
                [lm.x, lm.y, lm.z] for lm in results.face_landmarks.landmark
            ]).flatten()
        else:
            face = np.zeros(468 * 3)

        # Left Hand (21 landmarks * 3 coordinates = 63)
        if results.left_hand_landmarks:
            lh = np.array([
                [lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark
            ]).flatten()
        else:
            lh = np.zeros(21 * 3)

        # Right Hand (21 landmarks * 3 coordinates = 63)
        if results.right_hand_landmarks:
            rh = np.array([
                [lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark
            ]).flatten()
        else:
            rh = np.zeros(21 * 3)

        # Concatenate into one single flat vector of size 1662
        return np.concatenate([pose, face, lh, rh])

    def has_hands_detected(self, results) -> bool:
        """
        Helper utility checking if at least one hand is currently detected in frame.
        """
        if results is None:
            return False
        return (results.left_hand_landmarks is not None) or (results.right_hand_landmarks is not None)

landmark_extractor = LandmarkExtractor()
