from ai_engine.schemas.telemetry_schema import MotionTelemetryData, ComponentMotionMetrics

class MotionMetricsCalculator:
    def compile_metrics(self, lh_kin: dict, rh_kin: dict, pose_kin: dict, face_kin: dict) -> ComponentMotionMetrics:
        """
        Assembles component kinematic dictionaries into Pydantic models.
        """
        return ComponentMotionMetrics(
            left_hand=MotionTelemetryData(**lh_kin),
            right_hand=MotionTelemetryData(**rh_kin),
            pose=MotionTelemetryData(**pose_kin),
            face=MotionTelemetryData(**face_kin)
        )

motion_metrics_calc = MotionMetricsCalculator()
