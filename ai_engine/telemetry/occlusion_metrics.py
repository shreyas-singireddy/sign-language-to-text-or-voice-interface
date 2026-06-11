from ai_engine.schemas.landmark_schema import FrameLandmarkData
from ai_engine.schemas.telemetry_schema import OcclusionTelemetryData

class OcclusionMetricsCalculator:
    def calculate(self, frame_data: FrameLandmarkData) -> OcclusionTelemetryData:
        """
        Detects coordinate cutoff boundaries and missing landmarks.
        """
        hand_outside = False
        missing_lms = False
        body_cutoff = False
        partial_face = False

        # 1. Hands outside frame boundaries check (X range [0.0 - 1.0], Y range [0.0 - 1.0])
        # Check centers
        for hand in (frame_data.left_hand, frame_data.right_hand):
            if hand.present:
                c = hand.center
                if c.x < 0.05 or c.x > 0.95 or c.y < 0.05 or c.y > 0.95:
                    hand_outside = True
            else:
                missing_lms = True

        # 2. Body cutoff check: shoulders or elbows out of frame
        if frame_data.pose.present and len(frame_data.pose.landmarks) > 15:
            # Pose index 11 (L shoulder), 12 (R shoulder), 13 (L elbow), 14 (R elbow)
            for idx in (11, 12, 13, 14):
                p = frame_data.pose.landmarks[idx]
                if p.x < 0.01 or p.x > 0.99 or p.y < 0.01 or p.y > 0.99:
                    body_cutoff = True
                if p.visibility < 0.5:
                    missing_lms = True
        else:
            body_cutoff = True
            missing_lms = True

        # 3. Partial face check: eyes/mouth missing
        if frame_data.face.present:
            if frame_data.face.visibility < 0.7:
                partial_face = True
        else:
            partial_face = True

        # Compute occlusion percentage
        occlusion_count = 0
        total_checks = 4
        if hand_outside: occlusion_count += 1
        if partial_face: occlusion_count += 1
        if body_cutoff: occlusion_count += 1
        if missing_lms: occlusion_count += 1

        occlusion_pct = (occlusion_count / total_checks) * 100.0
        
        # Tracking loss is proportional to occlusion and missing landmarks
        tracking_loss = 0.0
        if not frame_data.left_hand.present and not frame_data.right_hand.present:
            tracking_loss += 50.0
        if not frame_data.pose.present:
            tracking_loss += 30.0
        if not frame_data.face.present:
            tracking_loss += 20.0

        return OcclusionTelemetryData(
            occlusion_percentage=round(occlusion_pct, 2),
            tracking_loss_percentage=round(tracking_loss, 2),
            hand_outside_frame=hand_outside,
            partial_face=partial_face,
            missing_landmarks=missing_lms,
            body_cutoff=body_cutoff
        )

occlusion_metrics_calc = OcclusionMetricsCalculator()
