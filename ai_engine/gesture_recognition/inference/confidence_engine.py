import numpy as np
from typing import List, Dict, Any

class ConfidenceEngine:
    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.prediction_history: List[str] = []

    def calculate_confidence(self, 
                             raw_prob: float, 
                             predicted_label: str,
                             tracking_stability: float, 
                             visibility_score: float) -> float:
        """
        Calculates final combined confidence score (0-100%).
        Factors:
            1. Raw classifier confidence (softmax probability).
            2. Temporal consistency (stable predictions over rolling history).
            3. Landmark tracking stability.
            4. Landmark visibility score.
        """
        # Append prediction to history
        self.prediction_history.append(predicted_label)
        if len(self.prediction_history) > self.history_size:
            self.prediction_history.pop(0)

        # 1. Raw Confidence
        raw_factor = raw_prob

        # 2. Temporal Consistency (percentage of frames in history matching current prediction)
        if len(self.prediction_history) > 0:
            matching_frames = sum(1 for label in self.prediction_history if label == predicted_label)
            consistency_factor = matching_frames / len(self.prediction_history)
        else:
            consistency_factor = 1.0

        # 3. Tracking Stability (scaled 0-1.0)
        stability_factor = max(0.0, min(1.0, tracking_stability / 100.0))

        # 4. Visibility factor
        visibility_factor = max(0.0, min(1.0, visibility_score / 100.0))

        # Combined weighted score:
        # 40% raw classifier, 30% consistency, 20% tracking stability, 10% visibility
        combined = (raw_factor * 0.40) + (consistency_factor * 0.30) + (stability_factor * 0.20) + (visibility_factor * 0.10)
        
        # Scale to 0-100%
        return round(float(combined) * 100.0, 2)

    def clear(self):
        self.prediction_history.clear()

confidence_engine = ConfidenceEngine()
