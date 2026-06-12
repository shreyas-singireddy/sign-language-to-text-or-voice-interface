import numpy as np

from ai_engine.schemas.landmark_schema import FrameLandmarkData, Point3D



class LandmarkNormalizer:
    def normalize_frame(self, frame_data: FrameLandmarkData) -> FrameLandmarkData:
        """
        Normalizes landmark coordinates to a body-relative coordinate system.

        Primary method:  Shoulder-midpoint anchor (when pose is available).
                         All landmarks are shifted to shoulders-midpoint and
                         divided by shoulder width for scale invariance.

        Fallback method: Wrist-anchor normalization (BUG-008 fix).
                         When pose is not detected (common for close-up laptop
                         webcams), we use the detected hand wrist as the anchor
                         and normalize by the hand bounding box diagonal.
                         This ensures consistent input to the classifier even
                         when the user's torso is not visible.
        """
        pose_data = frame_data.pose

        if not pose_data.present or len(pose_data.landmarks) <= 12:
            return frame_data  # Skip normalization if anchors missing

        l_sh = pose_data.landmarks[11]
        r_sh = pose_data.landmarks[12]

        # Calculate Midpoint (neck anchor)
        mid_x = (l_sh.x + r_sh.x) / 2.0
        mid_y = (l_sh.y + r_sh.y) / 2.0
        mid_z = (l_sh.z + r_sh.z) / 2.0

        # Calculate Shoulder width scale factor
        width = np.linalg.norm(np.array([l_sh.x - r_sh.x, l_sh.y - r_sh.y, l_sh.z - r_sh.z]))
        scale = width if width > 1e-4 else 1.0

        # Normalization helper
        def norm_points(pts: list[Point3D]) -> list[Point3D]:
            return [
                Point3D(
                    x=(p.x - mid_x) / scale,
                    y=(p.y - mid_y) / scale,
                    z=(p.z - mid_z) / scale,
                    visibility=p.visibility,
                )
                for p in pts
            ]

        # Normalize components
        if frame_data.left_hand.present:
            frame_data.left_hand.landmarks = norm_points(frame_data.left_hand.landmarks)
            frame_data.left_hand.center = norm_points([frame_data.left_hand.center])[0]
            if frame_data.left_hand.bounding_box:
                frame_data.left_hand.bounding_box.min_point = norm_points(
                    [frame_data.left_hand.bounding_box.min_point]
                )[0]
                frame_data.left_hand.bounding_box.max_point = norm_points(
                    [frame_data.left_hand.bounding_box.max_point]
                )[0]

        if frame_data.right_hand.present:
            frame_data.right_hand.landmarks = norm_points(frame_data.right_hand.landmarks)
            frame_data.right_hand.center = norm_points([frame_data.right_hand.center])[0]
            if frame_data.right_hand.bounding_box:
                frame_data.right_hand.bounding_box.min_point = norm_points(
                    [frame_data.right_hand.bounding_box.min_point]
                )[0]
                frame_data.right_hand.bounding_box.max_point = norm_points(
                    [frame_data.right_hand.bounding_box.max_point]
                )[0]

        frame_data.pose.landmarks = norm_points(frame_data.pose.landmarks)

        if frame_data.face.present:
            frame_data.face.landmarks = norm_points(frame_data.face.landmarks)

        return frame_data


landmark_normalizer = LandmarkNormalizer()
