try:
    import mediapipe as mp
except ImportError:
    mp = None

from ai_engine.utils.cv2_guard import cv2
import numpy as np

from config.config import (
    MP_MIN_DETECTION_CONFIDENCE,
    MP_MIN_TRACKING_CONFIDENCE,
    MP_STATIC_IMAGE_MODE,
)
from config.logger import setup_logger

logger = setup_logger("ai_engine.cv.holistic")


class MediaPipeHolisticManager:
    def __init__(self):
        self.mp_holistic = None
        self.holistic = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Loads MediaPipe modules and initializes Holistic model.
        """
        if self._initialized:
            return True

        if mp is None:
            logger.error("MediaPipe library is not installed or cannot be imported.")
            return False

        try:
            logger.info("Initializing MediaPipe Holistic Model...")
            self.mp_holistic = mp.solutions.holistic
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles

            # Setup holistic model
            self.holistic = self.mp_holistic.Holistic(
                static_image_mode=MP_STATIC_IMAGE_MODE,
                min_detection_confidence=MP_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=MP_MIN_TRACKING_CONFIDENCE,
            )
            self._initialized = True
            logger.info("MediaPipe Holistic Model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe Holistic: {e}")
            return False

    def process_frame(self, frame_bgr: np.ndarray):
        """
        Processes BGR image and extracts raw landmarks.
        Returns:
            results: MediaPipe results object, or None if uninitialized.
        """
        if not self._initialized:
            if not self.initialize():
                return None

        # Convert the BGR image to RGB before processing.
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame_rgb.flags.writeable = False
        results = self.holistic.process(frame_rgb)
        frame_rgb.flags.writeable = True

        return results

    def draw_landmarks(self, frame_bgr: np.ndarray, results) -> np.ndarray:
        """
        Draws skeleton overlays on the frame.
        """
        if not self._initialized or results is None:
            return frame_bgr

        annotated_image = frame_bgr.copy()

        # Draw face mesh connections
        if results.face_landmarks:
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=results.face_landmarks,
                connections=self.mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style(),
            )

        # Draw pose connections
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=results.pose_landmarks,
                connections=self.mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style(),
            )

        # Draw left hand connections
        if results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=results.left_hand_landmarks,
                connections=self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style(),
            )

        # Draw right hand connections
        if results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=results.right_hand_landmarks,
                connections=self.mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style(),
            )

        return annotated_image

    def close(self):
        """
        Closes the holistic model resources.
        """
        if self.holistic is not None:
            logger.info("Closing MediaPipe Holistic solution.")
            self.holistic.close()
            self.holistic = None
        self._initialized = False
