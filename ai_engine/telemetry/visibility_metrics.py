from ai_engine.schemas.landmark_schema import FrameLandmarkData
from ai_engine.schemas.telemetry_schema import VisibilityTelemetryData


class VisibilityMetricsCalculator:
    def calculate(self, frame_data: FrameLandmarkData) -> VisibilityTelemetryData:
        """
        Calculates visibility scores for each tracking component.
        """
        lh_vis = 1.0 if frame_data.left_hand.present else 0.0
        rh_vis = 1.0 if frame_data.right_hand.present else 0.0
        face_vis = frame_data.face.visibility if frame_data.face.present else 0.0

        # Pose visibility: mean visibility of shoulders, elbows, wrists, hips
        pose_vis = 0.0
        if frame_data.pose.present and len(frame_data.pose.landmarks) > 0:
            # We filter standard landmark visibility indexes (0 to 33)
            pose_vis = sum(lm.visibility for lm in frame_data.pose.landmarks) / len(
                frame_data.pose.landmarks
            )

        # Overall visibility [0 - 100]
        # Sum of visibilities scaled: hands represent 50% of weight, pose 30%, face 20%
        hands_weight = (lh_vis + rh_vis) / 2.0
        overall = (hands_weight * 50.0) + (pose_vis * 30.0) + (face_vis * 20.0)

        return VisibilityTelemetryData(
            left_hand_visibility=lh_vis,
            right_hand_visibility=rh_vis,
            face_visibility=face_vis,
            pose_visibility=round(pose_vis, 4),
            overall_visibility=round(overall, 2),
        )


visibility_metrics_calc = VisibilityMetricsCalculator()
