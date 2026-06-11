import numpy as np
from typing import List
from ai_engine.schemas.landmark_schema import Point3D, FrameLandmarkData


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

        # ── Primary: Shoulder anchor normalization ────────────────────────────
        if pose_data.present and len(pose_data.landmarks) > 12:
            l_sh = pose_data.landmarks[11]
            r_sh = pose_data.landmarks[12]

            mid_x = (l_sh.x + r_sh.x) / 2.0
            mid_y = (l_sh.y + r_sh.y) / 2.0
            mid_z = (l_sh.z + r_sh.z) / 2.0

            width = np.linalg.norm(
                np.array([l_sh.x - r_sh.x, l_sh.y - r_sh.y, l_sh.z - r_sh.z])
            )
            scale = width if width > 1e-4 else 1.0

            def norm_points(pts: List[Point3D]) -> List[Point3D]:
                return [
                    Point3D(
                        x=(p.x - mid_x) / scale,
                        y=(p.y - mid_y) / scale,
                        z=(p.z - mid_z) / scale,
                        visibility=p.visibility
                    ) for p in pts
                ]

            if frame_data.left_hand.present:
                frame_data.left_hand.landmarks = norm_points(frame_data.left_hand.landmarks)
                frame_data.left_hand.center = norm_points([frame_data.left_hand.center])[0]
                if frame_data.left_hand.bounding_box:
                    frame_data.left_hand.bounding_box.min_point = norm_points([frame_data.left_hand.bounding_box.min_point])[0]
                    frame_data.left_hand.bounding_box.max_point = norm_points([frame_data.left_hand.bounding_box.max_point])[0]

            if frame_data.right_hand.present:
                frame_data.right_hand.landmarks = norm_points(frame_data.right_hand.landmarks)
                frame_data.right_hand.center = norm_points([frame_data.right_hand.center])[0]
                if frame_data.right_hand.bounding_box:
                    frame_data.right_hand.bounding_box.min_point = norm_points([frame_data.right_hand.bounding_box.min_point])[0]
                    frame_data.right_hand.bounding_box.max_point = norm_points([frame_data.right_hand.bounding_box.max_point])[0]

            frame_data.pose.landmarks = norm_points(frame_data.pose.landmarks)

            if frame_data.face.present:
                frame_data.face.landmarks = norm_points(frame_data.face.landmarks)

            return frame_data

        # ── Fallback: Wrist-anchor normalization (BUG-008 fix) ────────────────
        # When shoulders are not detected, normalize each hand relative to its
        # own wrist (landmark index 0) and scale by its bounding-box diagonal.
        for hand_data in [frame_data.right_hand, frame_data.left_hand]:
            if not hand_data.present or len(hand_data.landmarks) < 21:
                continue

            wrist = hand_data.landmarks[0]
            wrist_x, wrist_y, wrist_z = wrist.x, wrist.y, wrist.z

            # Scale: bounding box diagonal of the hand
            xs = [p.x for p in hand_data.landmarks]
            ys = [p.y for p in hand_data.landmarks]
            zs = [p.z for p in hand_data.landmarks]
            diag = np.linalg.norm(
                np.array([max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)])
            )
            scale = diag if diag > 1e-4 else 1.0

            hand_data.landmarks = [
                Point3D(
                    x=(p.x - wrist_x) / scale,
                    y=(p.y - wrist_y) / scale,
                    z=(p.z - wrist_z) / scale,
                    visibility=p.visibility
                ) for p in hand_data.landmarks
            ]

            # Recompute center in normalized space
            n_xs = [p.x for p in hand_data.landmarks]
            n_ys = [p.y for p in hand_data.landmarks]
            n_zs = [p.z for p in hand_data.landmarks]
            if hand_data.center:
                hand_data.center.x = float(np.mean(n_xs))
                hand_data.center.y = float(np.mean(n_ys))
                hand_data.center.z = float(np.mean(n_zs))

        return frame_data


landmark_normalizer = LandmarkNormalizer()
