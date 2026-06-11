import numpy as np

from ai_engine.schemas.telemetry_schema import StabilityTelemetryData


class StabilityMetricsCalculator:
    def __init__(self):
        self.prev_landmarks = None

    def calculate(
        self, raw_coords: np.ndarray, smoothed_coords: np.ndarray
    ) -> StabilityTelemetryData:
        """
        Evaluates jitter and consistency.
        """
        # Jitter: difference between smoothed and raw coordinates
        jitter = float(np.mean(np.abs(raw_coords - smoothed_coords)))

        # Frame consistency: coordinate distance difference from previous frame
        consistency = 1.0
        if self.prev_landmarks is not None:
            diff = float(np.mean(np.abs(smoothed_coords - self.prev_landmarks)))
            consistency = max(0.0, 1.0 - diff)

        self.prev_landmarks = smoothed_coords.copy()

        # Stability rating [0 - 100]
        # Low jitter and high consistency results in stability ~100
        stability_rating = 100.0 * (1.0 - min(1.0, jitter * 50.0)) * consistency

        return StabilityTelemetryData(
            tracking_stability=round(stability_rating, 2),
            landmark_jitter=round(jitter, 5),
            frame_consistency=round(consistency, 4),
        )


stability_metrics_calc = StabilityMetricsCalculator()
