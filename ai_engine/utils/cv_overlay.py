"""
SignBridge AI — Computer Vision Overlay Utility
================================================
Provides custom annotation drawings for rendering hand skeletons, pose connections,
hand bounding boxes, and real-time prediction overlays using OpenCV.
"""

import numpy as np

from ai_engine.utils.cv2_guard import cv2

# Hand connections indices
HAND_CONNECTIONS = [
    # Thumb
    (0, 1), (1, 2), (2, 3), (3, 4),
    # Index finger
    (5, 6), (6, 7), (7, 8),
    # Middle finger
    (9, 10), (10, 11), (11, 12),
    # Ring finger
    (13, 14), (14, 15), (15, 16),
    # Pinky
    (17, 18), (18, 19), (19, 20),
    # Palm/knuckle connections
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
]

# Pose key connections (Shoulders, Elbows, Wrists)
POSE_CONNECTIONS = [
    (11, 12),  # Shoulder to Shoulder
    (11, 13), (13, 15),  # Left arm
    (12, 14), (14, 16)   # Right arm
]


def draw_skeleton_and_telemetry(
    frame: np.ndarray,
    landmarks,
    prediction_data: dict,
    fps: float,
    latency_ms: float
) -> np.ndarray:
    """
    Annotates the given image frame with hand skeletons, pose joints, bounding boxes,
    and prediction stats.

    Args:
        frame: OpenCV image frame (BGR format)
        landmarks: FrameLandmarkData object containing left_hand, right_hand, and pose
        prediction_data: Dict with 'prediction' and 'confidence' keys
        fps: Current camera frame rate
        latency_ms: Inference execution latency
    """
    if frame is None or cv2 is None:
        return frame

    annotated_frame = frame.copy()
    h, w, _ = annotated_frame.shape

    # 1. Draw Pose Skeletons (Key joints only to avoid clutter)
    if landmarks.pose and landmarks.pose.present:
        pts = landmarks.pose.landmarks
        # Draw connections
        for conn in POSE_CONNECTIONS:
            p1_idx, p2_idx = conn
            if p1_idx < len(pts) and p2_idx < len(pts):
                pt1, pt2 = pts[p1_idx], pts[p2_idx]
                if pt1.visibility > 0.5 and pt2.visibility > 0.5:
                    x1, y1 = int(pt1.x * w), int(pt1.y * h)
                    x2, y2 = int(pt2.x * w), int(pt2.y * h)
                    cv2.line(annotated_frame, (x1, y1), (x2, y2), (240, 20, 20), 2)  # Blue line

        # Draw joint circles
        for idx in [11, 12, 13, 14, 15, 16]:
            if idx < len(pts):
                pt = pts[idx]
                if pt.visibility > 0.5:
                    cx, cy = int(pt.x * w), int(pt.y * h)
                    cv2.circle(annotated_frame, (cx, cy), 5, (20, 20, 240), -1)  # Red circle

    # 2. Draw Hands
    active_hand_present = False
    for hand_name, hand_data in [("Left Hand", landmarks.left_hand), ("Right Hand", landmarks.right_hand)]:
        if hand_data and hand_data.present and len(hand_data.landmarks) >= 21:
            active_hand_present = True
            pts = hand_data.landmarks
            color_skeleton = (40, 200, 40) if hand_name == "Right Hand" else (200, 200, 40)

            # Find 2D bounding box
            x_coords = [int(p.x * w) for p in pts]
            y_coords = [int(p.y * h) for p in pts]
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)

            # Draw bounding box (with slight padding)
            pad = 12
            bx1, by1 = max(0, min_x - pad), max(0, min_y - pad)
            bx2, by2 = min(w, max_x + pad), min(h, max_y + pad)
            cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (20, 180, 240), 2)

            # Draw hand label and center near the wrist
            wrist = pts[0]
            wx, wy = int(wrist.x * w), int(wrist.y * h)
            cv2.circle(annotated_frame, (wx, wy), 7, (240, 240, 20), -1)  # Cyan wrist anchor

            # Draw connection lines
            for conn in HAND_CONNECTIONS:
                p1_idx, p2_idx = conn
                x1, y1 = x_coords[p1_idx], y_coords[p1_idx]
                x2, y2 = x_coords[p2_idx], y_coords[p2_idx]
                cv2.line(annotated_frame, (x1, y1), (x2, y2), color_skeleton, 2)

            # Draw joint circles
            for cx, cy in zip(x_coords, y_coords):
                cv2.circle(annotated_frame, (cx, cy), 4, (10, 10, 10), -1)
                cv2.circle(annotated_frame, (cx, cy), 3, (255, 255, 255), -1)

            # Draw prediction text above the hand bounding box
            pred_label = prediction_data.get("prediction", "IDLE")
            pred_conf = prediction_data.get("confidence", 0.0)
            if pred_label not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
                label_text = f"{pred_label} ({pred_conf * 100:.1f}%)"
                cv2.putText(
                    annotated_frame,
                    label_text,
                    (bx1, max(20, by1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (20, 240, 20),
                    2,
                    cv2.LINE_AA
                )

    # 3. Global AI HUD Overlay (Top Left)
    hud_x, hud_y = 10, 10

    status_str = "Active" if active_hand_present else "Search"
    status_color = (40, 240, 40) if active_hand_present else (40, 120, 240)

    # Render HUD stats
    cv2.putText(annotated_frame, f"Tracking: {status_str}", (hud_x + 10, hud_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2, cv2.LINE_AA)
    cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (hud_x + 10, hud_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 250, 250), 1, cv2.LINE_AA)
    cv2.putText(annotated_frame, f"Latency: {latency_ms:.1f} ms", (hud_x + 10, hud_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 250, 250), 1, cv2.LINE_AA)

    # Clean borders for hud box
    cv2.rectangle(annotated_frame, (hud_x, hud_y), (hud_x + 220, hud_y + 80), (120, 120, 120), 1)

    return annotated_frame
