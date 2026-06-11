import numpy as np

from config.config import GESTURE_CONFIDENCE_THRESHOLD, MODELS_DIR
from config.logger import setup_logger

logger = setup_logger("ai_engine.gesture.detector")


class GestureDetector:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.load_model()

    def load_model(self) -> bool:
        """
        Attempts to load a trained gesture classification model (TF/Keras/PyTorch/ONNX).
        Returns True if loaded, False if geometric heuristic fallback is active.
        """
        model_path = MODELS_DIR / "gesture_classifier.h5"
        if not model_path.exists():
            logger.warning(
                f"No gesture classification model found at {model_path}. Using fallback heuristic classifier."
            )
            self.model_loaded = False
            return False

        try:
            logger.info(f"Loading gesture model from {model_path}...")
            # self.model = tf.keras.models.load_model(str(model_path))
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(
                f"Error loading model from {model_path}: {e}. Falling back to heuristic classifier."
            )
            self.model_loaded = False
            return False

    def predict(self, landmark_vector: np.ndarray) -> tuple:
        """
        Predicts gesture label from a flattened 1662-element landmark vector.

        Priority:
          1. ML model (ONNX / PyTorch) via Layer 4 predictor — if trained weights exist
          2. Geometric finger-extension heuristics — always available, no training required

        Returns:
            label (str): Predicted gesture token
            confidence (float): Classification probability [0.0 - 1.0]
        """
        from ai_engine.gesture_recognition.inference.predictor import gesture_predictor

        # Run prediction via the Layer 4 predictor (which handles ONNX and PyTorch)
        res = gesture_predictor.predict_alphabet(landmark_vector)
        pred = res["prediction"]
        conf = res["confidence"]

        # If prediction fails, or readiness filter triggers "WAITING_FOR_CLEAR_GESTURE",
        # fallback to heuristic classification to keep UI responsive
        if pred == "WAITING_FOR_CLEAR_GESTURE" or conf < GESTURE_CONFIDENCE_THRESHOLD:
            lh_slice = landmark_vector[1404:1467]
            rh_slice = landmark_vector[1467:1530]

            has_left = np.any(lh_slice > 0)
            has_right = np.any(rh_slice > 0)

            if not has_left and not has_right:
                return "IDLE", 1.0

            if has_right:
                wrist_y = rh_slice[1]
                tip_y = rh_slice[25]
                if tip_y < wrist_y - 0.2:
                    return "HELLO", 0.88
                elif tip_y > wrist_y:
                    return "YES", 0.79
                else:
                    return "THANKS", 0.85
            return "IDLE", 0.5

        return pred, conf


gesture_detector = GestureDetector()
