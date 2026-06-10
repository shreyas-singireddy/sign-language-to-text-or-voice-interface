import collections
import numpy as np
from config.config import MODELS_DIR, SEQUENCE_BUFFER_SIZE
from config.logger import setup_logger

logger = setup_logger("ai_engine.sequence.model")

class SequenceModel:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.buffer = collections.deque(maxlen=SEQUENCE_BUFFER_SIZE)
        self.load_model()

    def load_model(self) -> bool:
        """
        Loads sequence model (e.g., LSTM / GRU / Transformer).
        """
        model_path = MODELS_DIR / "sequence_model.h5"
        if not model_path.exists():
            logger.warning(f"No sequence model found at {model_path}. Running sequence assembly heuristics.")
            self.model_loaded = False
            return False

        try:
            logger.info(f"Loading sequence model from {model_path}...")
            # self.model = tf.keras.models.load_model(str(model_path))
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Error loading sequence model: {e}")
            self.model_loaded = False
            return False

    def add_to_buffer(self, landmark_vector: np.ndarray, gesture_label: str):
        """
        Appends frame data to the temporal sliding window.
        """
        self.buffer.append((landmark_vector, gesture_label))

    def decode_sequence(self) -> list:
        """
        Decodes the sliding frame buffer into a list of words or gestures.
        """
        if len(self.buffer) < 5:
            return []

        if self.model_loaded and self.model is not None:
            try:
                # Prepare sequence tensor (e.g., shape (1, SEQUENCE_BUFFER_SIZE, 1662))
                seq_data = np.array([item[0] for item in self.buffer])
                seq_data = np.expand_dims(seq_data, axis=0)
                # output = self.model.predict(seq_data)
                # decode logic ...
                return ["HELLO"]
            except Exception as e:
                logger.error(f"Failed to run sequence model inference: {e}")

        # Heuristic Sequence Assembly
        # We group continuous blocks of matching labels in the buffer and filter out "IDLE".
        # This acts as a rolling filter to debounce classifications.
        assembled = []
        last_label = None
        consecutive_count = 0
        min_consecutive_frames = 10  # Must be held stable for 10 frames to registers

        for _, label in self.buffer:
            if label == "IDLE":
                last_label = None
                consecutive_count = 0
                continue
                
            if label == last_label:
                consecutive_count += 1
            else:
                last_label = label
                consecutive_count = 1

            if consecutive_count == min_consecutive_frames:
                # Add to translation list if it's not a direct duplicate of the last registered gesture
                if not assembled or assembled[-1] != label:
                    assembled.append(label)
                    
        return assembled

    def clear_buffer(self):
        """Clears the temporal frame cache."""
        self.buffer.clear()

sequence_model = SequenceModel()
