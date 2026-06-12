import numpy as np

from config.logger import setup_logger

logger = setup_logger("ai_engine.motion_analysis")


class MotionAnalyser:
    def __init__(self, buffer_size: int = 10):
        self.buffer_size = buffer_size
        self.coordinate_history = []

    def compute_stability_index(self, landmarks: np.ndarray) -> float:
        """
        Computes standard deviation of coordinate coordinates over a short history window.
        A low variance indicates high stability (still postures), high variance indicates motion/jitter.
        """
        self.coordinate_history.append(landmarks)
        if len(self.coordinate_history) > self.buffer_size:
            self.coordinate_history.pop(0)

        if len(self.coordinate_history) < 2:
            return 1.0

        # Calculate standard deviation along temporal axis
        std_dev = np.std(self.coordinate_history, axis=0)
        mean_std = float(np.mean(std_dev))

        # Stability = 1 / (1 + mean_std)
        stability = 1.0 / (1.0 + (mean_std * 10.0))
        return round(stability, 4)

    def calculate_occlusion_score(self, mp_results) -> float:
        """
        Determines the percentage of joints hidden/occluded in the frame.
        Pose has 33 landmarks with visibility attributes.
        """
        if mp_results is None or not hasattr(mp_results, "pose_landmarks") or mp_results.pose_landmarks is None:
            return 1.0  # 100% occluded / missing

        low_visibility_count = 0
        total_points = len(mp_results.pose_landmarks.landmark)

        for lm in mp_results.pose_landmarks.landmark:
            if lm.visibility < 0.5:
                low_visibility_count += 1

        return round(low_visibility_count / total_points, 4)

    def calculate_activity_index(self, mean_velocity: float) -> float:
        """
        Scales average velocity to represent general motion activity levels.
        """
        # Scale to range [0.0 - 1.0]
        activity = min(1.0, mean_velocity * 100.0)
        return round(activity, 4)

    def evaluate(self, landmarks: np.ndarray, mean_velocity: float, mp_results) -> dict:
        """
        Aggregates motion analytics.
        """
        stability = self.compute_stability_index(landmarks)
        occlusion = self.calculate_occlusion_score(mp_results)
        activity = self.calculate_activity_index(mean_velocity)

        # Basic tracking health rating
        tracking_health = round(max(0.0, 1.0 - (occlusion * 0.7) - (stability * 0.1)), 4)

        return {
            "stability_index": stability,
            "occlusion_score": occlusion,
            "activity_index": activity,
            "tracking_health": tracking_health,
        }


motion_analyser = MotionAnalyser()
