import numpy as np

from config.logger import setup_logger

logger = setup_logger("ai_engine.inference_preparation")


class InferencePreprocessor:
    def __init__(self, sequence_length: int = 30, feature_size: int = 1662):
        self.sequence_length = sequence_length
        self.feature_size = feature_size

    def pad_sequence(self, raw_sequence: list) -> np.ndarray:
        """
        Pads or truncates a sequence of frames to match model input shapes (e.g. 30 frames).
        Input: list of vectors of shape (1662,)
        Output: numpy array of shape (1, 30, 1662) for LSTM/Transformer input.
        """
        seq_len = len(raw_sequence)

        if seq_len == 0:
            return np.zeros((1, self.sequence_length, self.feature_size))

        if seq_len >= self.sequence_length:
            # Truncate to the last N frames
            formatted = np.array(raw_sequence[-self.sequence_length :])
        else:
            # Zero-pad at the beginning
            padding = np.zeros((self.sequence_length - seq_len, self.feature_size))
            formatted = np.vstack([padding, np.array(raw_sequence)])

        # Add batch dimension: shape (1, N, F)
        return np.expand_dims(formatted, axis=0)

    def assess_data_readiness(self, landmarks: np.ndarray, tracking_health: float) -> dict:
        """
        Grades coordinate and feature quality metrics for model training compatibility.
        """
        # Assess structural coverage (hands present is high readiness)
        lh_slice = landmarks[1404:1467]
        rh_slice = landmarks[1467:1530]
        hands_detected = np.any(lh_slice > 0) or np.any(rh_slice > 0)

        # Readiness calculations
        data_quality = 0.95 if tracking_health > 0.8 else tracking_health
        feature_quality = 0.90 if hands_detected else 0.40
        readiness_score = (data_quality + feature_quality + tracking_health) / 3.0

        return {
            "data_quality_score": round(data_quality, 2),
            "feature_quality_score": round(feature_quality, 2),
            "tracking_stability_score": round(tracking_health, 2),
            "is_training_ready": readiness_score > 0.7,
            "readiness_grade": ("EXCELLENT" if readiness_score > 0.8 else "GOOD" if readiness_score > 0.6 else "POOR"),
        }


inference_preprocessor = InferencePreprocessor()
