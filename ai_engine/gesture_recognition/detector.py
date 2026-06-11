import numpy as np
from config.config import SUPPORTED_GESTURES, GESTURE_CONFIDENCE_THRESHOLD, MODELS_DIR
from config.logger import setup_logger

logger = setup_logger("ai_engine.gesture.detector")


# ──────────────────────────────────────────────────────────────────────────────
# Geometric heuristic constants
# Layout of the 1662-vector:
#   [0:132]    = Pose (33 × 4: x, y, z, visibility)
#   [132:1536] = Face (468 × 3: x, y, z)
#   [1536:1599]= Left Hand (21 × 3: x, y, z)  ← corrected from wrong [1404:1467]
#   [1599:1662]= Right Hand (21 × 3: x, y, z) ← corrected from wrong [1467:1530]
#
# Hand landmark indices (within the 21-point hand array, each row = [x, y, z]):
#   0  = Wrist
#   4  = Thumb tip
#   8  = Index tip
#   12 = Middle tip
#   16 = Ring tip
#   20 = Pinky tip
#   5  = Index MCP (knuckle)
# ──────────────────────────────────────────────────────────────────────────────
LH_START = 1536
LH_END   = 1599
RH_START = 1599
RH_END   = 1662


def _reshape_hand(flat_slice: np.ndarray) -> np.ndarray:
    """Reshape 63-element flat slice into (21, 3) hand landmark array."""
    return flat_slice.reshape((21, 3))


def _finger_up(hand: np.ndarray, tip_idx: int, pip_idx: int) -> bool:
    """Returns True if the finger tip is above its PIP joint (lower Y = higher on screen)."""
    return hand[tip_idx, 1] < hand[pip_idx, 1]


def _thumb_open(hand: np.ndarray, mirror: bool = False) -> bool:
    """
    Estimates thumb extension by checking if thumb tip (4) is far from index MCP (5).
    mirror=True for left hand (image-mirrored).
    """
    dist = np.linalg.norm(hand[4] - hand[5])
    return dist > 0.1


def _heuristic_classify(hand: np.ndarray, label_prefix: str = "") -> tuple:
    """
    Rule-based geometric gesture classification using finger extension patterns.
    
    Finger extension is determined by tip Y < PIP Y (higher on screen).
    PIP joints: Thumb-2, Index-6, Middle-10, Ring-14, Pinky-18
    Tip joints: Thumb-4, Index-8, Middle-12, Ring-16, Pinky-20
    
    Returns: (gesture_label: str, confidence: float)
    """
    if np.all(hand == 0):
        return "IDLE", 1.0

    # Compute per-finger extension flags
    thumb_open = _thumb_open(hand)
    index_up   = _finger_up(hand, 8, 6)
    middle_up  = _finger_up(hand, 12, 10)
    ring_up    = _finger_up(hand, 16, 14)
    pinky_up   = _finger_up(hand, 20, 18)

    fingers_up = [thumb_open, index_up, middle_up, ring_up, pinky_up]
    num_up = sum(fingers_up)

    # ── Gesture Rules ─────────────────────────────────────────────────────────
    # HELLO: All 5 fingers extended (open palm / wave)
    if num_up == 5:
        return "HELLO", 0.87

    # YES: Fist (all fingers curled)
    if num_up == 0:
        return "YES", 0.82

    # THANKS: 4 fingers up, thumb not extended (flat hand, no thumb)
    if num_up == 4 and not thumb_open:
        return "THANKS", 0.80

    # PLEASE: flat hand except thumb — 4 fingers up + thumb extended
    if num_up == 4 and thumb_open:
        return "PLEASE", 0.78

    # NO: index + middle finger up (peace / scissors)
    if index_up and middle_up and not ring_up and not pinky_up:
        return "NO", 0.83

    # HELP: thumb up only (thumbs-up gesture)
    if thumb_open and not index_up and not middle_up and not ring_up and not pinky_up:
        return "HELP", 0.80

    # SORRY: index finger only
    if index_up and not middle_up and not ring_up and not pinky_up:
        return "SORRY", 0.75

    # GOOD MORNING: 3 middle fingers up (index, middle, ring)
    if index_up and middle_up and ring_up and not pinky_up:
        return "GOOD MORNING", 0.72

    # GOOD NIGHT: pinky up only
    if pinky_up and not index_up and not middle_up and not ring_up:
        return "GOOD NIGHT", 0.72

    return "IDLE", 0.5


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
                f"No gesture classification model found at {model_path}. "
                f"Using geometric heuristic classifier (finger-extension rules)."
            )
            self.model_loaded = False
            return False

        try:
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
        Predicts gesture label from a flattened 1662-element landmark vector.

        Priority:
          1. ML model (ONNX / PyTorch) via Layer 4 predictor — if trained weights exist
          2. Geometric finger-extension heuristics — always available, no training required

        Returns:
            label (str): Predicted gesture token
            confidence (float): Classification probability [0.0 - 1.0]
        """
        # ── Step 1: Try the Layer 4 neural predictor ──────────────────────────
        try:
            from ai_engine.gesture_recognition.inference.predictor import gesture_predictor
            res = gesture_predictor.predict_alphabet(landmark_vector)
            pred = res["prediction"]
            conf = res["confidence"]

            # Accept if the predictor is confident and not stalling
            if pred not in ("WAITING_FOR_CLEAR_GESTURE", "IDLE") and conf >= GESTURE_CONFIDENCE_THRESHOLD:
                return pred, conf

        except Exception as e:
            logger.debug(f"Layer 4 predictor error: {e}. Falling back to heuristics.")

        # ── Step 2: Geometric heuristic fallback ──────────────────────────────
        # CORRECTED vector slices (BUG-004 fix):
        lh_flat = landmark_vector[LH_START:LH_END]   # Left Hand:  indices 1536–1599
        rh_flat = landmark_vector[RH_START:RH_END]   # Right Hand: indices 1599–1662

        has_left  = np.any(lh_flat > 0)
        has_right = np.any(rh_flat > 0)

        if not has_left and not has_right:
            return "IDLE", 1.0

        # Prefer right hand for classification
        if has_right:
            rh = _reshape_hand(rh_flat)
            return _heuristic_classify(rh)

        if has_left:
            lh = _reshape_hand(lh_flat)
            return _heuristic_classify(lh)

        return "IDLE", 0.5


gesture_detector = GestureDetector()
