import numpy as np
from config.config import SUPPORTED_GESTURES, GESTURE_CONFIDENCE_THRESHOLD, MODELS_DIR
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
        Returns True if loaded, False if fallback is active.
        """
        model_path = MODELS_DIR / "gesture_classifier.h5"
        if not model_path.exists():
            logger.warning(f"No gesture classification model found at {model_path}. Using fallback heuristic classifier.")
            self.model_loaded = False
            return False

        try:
            # Placeholder for actual model loading (e.g. tensorflow.keras.models.load_model)
            logger.info(f"Loading gesture model from {model_path}...")
            # self.model = tf.keras.models.load_model(str(model_path))
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {e}. Falling back to heuristic classifier.")
            self.model_loaded = False
            return False

    def predict(self, landmark_vector: np.ndarray) -> tuple:
        """
        Predicts gesture label from a flattened landmark vector.
        Returns:
            label (str): Predicted gesture token
            confidence (float): Classification probability [0.0 - 1.0]
        """
        if self.model_loaded and self.model is not None:
            try:
                # Add batch dimension
                input_data = np.expand_dims(landmark_vector, axis=0)
                predictions = self.model.predict(input_data, verbose=0)[0]
                idx = np.argmax(predictions)
                confidence = float(predictions[idx])
                
                if confidence >= GESTURE_CONFIDENCE_THRESHOLD:
                    return SUPPORTED_GESTURES[idx], confidence
                return "IDLE", confidence
            except Exception as e:
                logger.error(f"Inference error: {e}. Defaulting to heuristic fallback.")

        # Heuristic Mock Fallback
        # We analyze the hand landmark portions of the vector (Left Hand index 1404-1467, Right Hand 1467-1530)
        # If the hand landmark sum is 0, then no hands are in frame -> IDLE
        lh_slice = landmark_vector[1404:1467]
        rh_slice = landmark_vector[1467:1530]
        
        has_left = np.any(lh_slice > 0)
        has_right = np.any(rh_slice > 0)
        
        if not has_left and not has_right:
            return "IDLE", 1.0

        # Heuristic: return a random valid gesture for visualization when a hand is visible,
        # or use simple coordinate heuristics to simulate different gestures for demo.
        # Let's map different regions of right hand y-coords to different gestures to simulate interaction:
        if has_right:
            wrist_y = rh_slice[1] # Wrist y
            tip_y = rh_slice[25]  # Index finger tip y (approximate indexing)
            if tip_y < wrist_y - 0.2:
                # Hand raised high
                return "HELLO", 0.88
            elif tip_y > wrist_y:
                # Hand down
                return "YES", 0.79
            else:
                return "THANKS", 0.85
        
        return "IDLE", 0.5

gesture_detector = GestureDetector()
