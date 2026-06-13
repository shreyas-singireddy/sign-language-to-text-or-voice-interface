import numpy as np

from ai_engine.schemas.landmark_schema import FrameLandmarkData


def calculate_angle(a, b, c) -> float:
    """
    Calculates the angle in degrees at vertex b formed by points a, b, and c.
    Points a, b, and c are coordinate objects containing x, y, z attributes.
    """
    p_a = np.array([a.x, a.y, a.z])
    p_b = np.array([b.x, b.y, b.z])
    p_c = np.array([c.x, c.y, c.z])

    ba = p_a - p_b
    bc = p_c - p_b

    # Cosine formula
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-7)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.arccos(cosine_angle)
    return float(np.degrees(angle))

class ErrorDetectionEngine:
    def __init__(self):
        # Default reference joint angles (in degrees) for common signs
        self.reference_angles = {
            "hello": {
                "right_elbow": 140.0,
                "right_shoulder": 80.0,
                "fingers_spread": True
            },
            "thank_you": {
                "right_elbow": 60.0,
                "right_shoulder": 40.0,
                "fingers_spread": False
            },
            "greeting": {
                "right_elbow": 110.0,
                "right_shoulder": 50.0,
                "fingers_spread": True
            },
            "emergency": {
                "right_elbow": 90.0,
                "right_shoulder": 90.0,
                "left_elbow": 90.0,
                "left_shoulder": 90.0,
                "fingers_spread": True
            }
        }

    def detect_errors(self, frame_lms: FrameLandmarkData, target_sign: str) -> dict:
        """
        Runs joint alignment checks on pose/hand landmarks.
        Returns a dict highlighting deviations, error descriptions, and suggestions.
        """
        sign_key = target_sign.lower().strip()
        ref = self.reference_angles.get(sign_key)

        # If no explicit sign ref, provide general hand/posture statistics check
        if not ref:
            ref = {
                "right_elbow": 100.0,
                "right_shoulder": 60.0,
                "fingers_spread": True
            }

        deviations = []
        corrections = []

        # 1. Pose Joint Checks (Shoulders, Elbows)
        if frame_lms.pose.present and len(frame_lms.pose.landmarks) >= 17:
            lms = frame_lms.pose.landmarks

            # Right arm joints
            # Right shoulder (12), elbow (14), wrist (16)
            right_elbow_ang = calculate_angle(lms[12], lms[14], lms[16])
            # Right hip (24), shoulder (12), elbow (14)
            right_shoulder_ang = calculate_angle(lms[24], lms[12], lms[14])

            ref_elbow = ref.get("right_elbow", 100.0)
            ref_shoulder = ref.get("right_shoulder", 60.0)

            elbow_diff = abs(right_elbow_ang - ref_elbow)
            if elbow_diff > 25.0:
                deviations.append({
                    "joint": "Right Elbow Angle",
                    "actual": round(right_elbow_ang, 1),
                    "expected": round(ref_elbow, 1),
                    "variance": round(elbow_diff, 1)
                })
                if right_elbow_ang < ref_elbow:
                    corrections.append("Extend your right arm more outwards.")
                else:
                    corrections.append("Keep your right elbow slightly closer / more bent.")

            shoulder_diff = abs(right_shoulder_ang - ref_shoulder)
            if shoulder_diff > 25.0:
                deviations.append({
                    "joint": "Right Shoulder Elevation",
                    "actual": round(right_shoulder_ang, 1),
                    "expected": round(ref_shoulder, 1),
                    "variance": round(shoulder_diff, 1)
                })
                if right_shoulder_ang < ref_shoulder:
                    corrections.append("Raise your right arm higher.")
                else:
                    corrections.append("Lower your right shoulder/upper arm.")

        # 2. Hand Pose/Finger Spread Checks
        hand_present = frame_lms.right_hand.present
        hand_lms = frame_lms.right_hand.landmarks if hand_present else []

        if not hand_present and frame_lms.left_hand.present:
            hand_present = True
            hand_lms = frame_lms.left_hand.landmarks

        if hand_present and len(hand_lms) >= 21:
            # Check if fingers are spread or curled by calculating distance from wrist (0) to tips (4, 8, 12, 16, 20)
            tips = [4, 8, 12, 16, 20]
            wrist = hand_lms[0]

            distances = []
            for tip_idx in tips:
                tip = hand_lms[tip_idx]
                dist = np.linalg.norm(np.array([tip.x - wrist.x, tip.y - wrist.y, tip.z - wrist.z]))
                distances.append(float(dist))

            avg_extension = np.mean(distances)
            expected_spread = ref.get("fingers_spread", True)

            # Spread fingers average extension is higher (usually > 0.35 in normalized coords)
            is_spread = avg_extension > 0.35

            if expected_spread != is_spread:
                deviations.append({
                    "joint": "Hand Configuration",
                    "actual": "Spread" if is_spread else "Closed",
                    "expected": "Spread" if expected_spread else "Closed",
                    "variance": abs(avg_extension - 0.35)
                })
                if expected_spread:
                    corrections.append("Spread your fingers wide apart.")
                else:
                    corrections.append("Close your fingers together or form a flat palm.")
        elif not hand_present:
            deviations.append({
                "joint": "Hand Tracking",
                "actual": "Not In View",
                "expected": "Visible",
                "variance": 1.0
            })
            corrections.append("Bring your hand fully in front of the camera sensor.")

        # Compile final feedback structure
        success = len(deviations) == 0
        status = "Correct" if success else "Needs Correction"

        return {
            "status": status,
            "target_sign": target_sign,
            "deviations": deviations,
            "corrections": corrections,
            "overall_accuracy": max(0, 100 - len(deviations) * 20)
        }

error_detector = ErrorDetectionEngine()
