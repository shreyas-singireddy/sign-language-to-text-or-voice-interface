import numpy as np
from typing import Dict, Tuple, List, Any

def unpack_landmarks(flat_landmarks: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Unpacks a 1662 flat landmark array into structural sub-arrays:
    Returns:
        pose (33, 4) - x, y, z, visibility
        face (468, 3) - x, y, z
        left_hand (21, 3) - x, y, z
        right_hand (21, 3) - x, y, z
    """
    # Initialize defaults
    pose = np.zeros((33, 4))
    face = np.zeros((468, 3))
    left_hand = np.zeros((21, 3))
    right_hand = np.zeros((21, 3))
    
    if len(flat_landmarks) < 1662:
        return pose, face, left_hand, right_hand
        
    # Pose: 33 points * 4 elements = 132
    pose_flat = flat_landmarks[0:132]
    pose = pose_flat.reshape((33, 4))
    
    # Face: 468 points * 3 elements = 1404. Offset starts at 132. Ends at 132 + 1404 = 1536.
    face_flat = flat_landmarks[132:1536]
    face = face_flat.reshape((-1, 3))
    
    # Left hand: 21 points * 3 elements = 63. Offset starts at 1536. Ends at 1536 + 63 = 1599.
    lh_flat = flat_landmarks[1536:1599]
    left_hand = lh_flat.reshape((21, 3))
    
    # Right hand: 21 points * 3 elements = 63. Offset starts at 1599. Ends at 1599 + 63 = 1662.
    rh_flat = flat_landmarks[1599:1662]
    right_hand = rh_flat.reshape((21, 3))
    
    return pose, face, left_hand, right_hand

def compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Computes angle (in degrees) at vertex p2 between p1-p2 and p3-p2."""
    v1 = p1 - p2
    v2 = p3 - p2
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-6 or norm2 < 1e-6:
        return 180.0
    cos_theta = np.dot(v1, v2) / (norm1 * norm2)
    angle = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    return float(np.degrees(angle))

def extract_hand_features(hand: np.ndarray) -> Dict[str, Any]:
    """
    Computes finger curls and angles for a hand.
    Hand shape is (21, 3). Wrist is index 0.
    Fingers:
        Thumb: 0-1-2-3-4
        Index: 0-5-6-7-8
        Middle: 0-9-10-11-12
        Ring: 0-13-14-15-16
        Pinky: 0-17-18-19-20
    """
    features = {}
    if np.all(hand == 0):
        features["curls"] = [0.0] * 5
        features["joint_angles"] = [180.0] * 5
        features["pairwise_distances"] = [0.0] * 10
        return features

    # Finger curls (ratio of distance from tip to wrist over total length of finger)
    # Fingers tip indices: 4, 8, 12, 16, 20
    tips = [4, 8, 12, 16, 20]
    mcp_joints = [1, 5, 9, 13, 17]
    curls = []
    for tip, mcp in zip(tips, mcp_joints):
        dist_tip_wrist = np.linalg.norm(hand[tip] - hand[0])
        dist_mcp_wrist = np.linalg.norm(hand[mcp] - hand[0])
        # A curled finger has its tip close to MCP/wrist
        if dist_mcp_wrist > 1e-6:
            curls.append(float(dist_tip_wrist / (dist_mcp_wrist + 1e-6)))
        else:
            curls.append(1.0)
            
    features["curls"] = curls

    # Joint angles (MCP-PIP-DIP angles)
    # Indices:
    # Thumb: 2-3-4
    # Index: 6-7-8
    # Middle: 10-11-12
    # Ring: 14-15-16
    # Pinky: 18-19-20
    joint_angles = [
        compute_angle(hand[1], hand[2], hand[3]),
        compute_angle(hand[5], hand[6], hand[7]),
        compute_angle(hand[9], hand[10], hand[11]),
        compute_angle(hand[13], hand[14], hand[15]),
        compute_angle(hand[17], hand[18], hand[19])
    ]
    features["joint_angles"] = joint_angles

    # Pairwise fingertip distances (10 combinations)
    pairwise = []
    for i in range(len(tips)):
        for j in range(i+1, len(tips)):
            d = np.linalg.norm(hand[tips[i]] - hand[tips[j]])
            pairwise.append(float(d))
    features["pairwise_distances"] = pairwise

    return features

def extract_pose_features(pose: np.ndarray) -> Dict[str, Any]:
    """
    Computes joint angles for elbows and shoulders.
    Pose landmarks:
        11: Left Shoulder, 12: Right Shoulder
        13: Left Elbow,    14: Right Elbow
        15: Left Wrist,    16: Right Wrist
    """
    features = {}
    if np.all(pose == 0):
        features["left_elbow_angle"] = 180.0
        features["right_elbow_angle"] = 180.0
        features["shoulder_angle"] = 0.0
        features["arm_extension_left"] = 0.0
        features["arm_extension_right"] = 0.0
        return features

    # Extract 3D coordinates (first 3 columns)
    p3d = pose[:, :3]
    
    # Left Elbow Angle (11-13-15)
    features["left_elbow_angle"] = compute_angle(p3d[11], p3d[13], p3d[15])
    # Right Elbow Angle (12-14-16)
    features["right_elbow_angle"] = compute_angle(p3d[12], p3d[14], p3d[16])
    
    # Shoulder angle relative to horizontal
    shoulder_vector = p3d[12] - p3d[11]
    dx, dy = shoulder_vector[0], shoulder_vector[1]
    features["shoulder_angle"] = float(np.degrees(np.arctan2(dy, dx + 1e-6)))

    # Arm extension relative to shoulder width
    shoulder_width = np.linalg.norm(p3d[12] - p3d[11]) + 1e-6
    features["arm_extension_left"] = float(np.linalg.norm(p3d[15] - p3d[11]) / shoulder_width)
    features["arm_extension_right"] = float(np.linalg.norm(p3d[16] - p3d[12]) / shoulder_width)

    return features

def extract_face_features(face: np.ndarray) -> Dict[str, Any]:
    """
    Computes mouth openness and eyebrows alignment.
    Using landmark indexes:
        Lip upper/lower: 13, 14
        Lip left/right: 78, 308
    """
    features = {}
    if len(face) < 309 or np.all(face == 0):
        features["mouth_openness"] = 0.0
        features["eyebrow_tilt"] = 0.0
        return features

    # Mouth openness
    gap = np.linalg.norm(face[13] - face[14])
    width = np.linalg.norm(face[78] - face[308])
    features["mouth_openness"] = float(gap / (width + 1e-6))

    # Eyebrow height differential (simple proxy for eyebrow movement)
    # Left eyebrow corner 70, right eyebrow corner 300
    features["eyebrow_tilt"] = float(face[70, 1] - face[300, 1])

    return features

def compile_geometric_features(flat_landmarks: np.ndarray) -> np.ndarray:
    """
    Extracts and concatenates all landmark features into a single engineered feature vector.
    """
    pose, face, lh, rh = unpack_landmarks(flat_landmarks)
    
    lh_feats = extract_hand_features(lh)
    rh_feats = extract_hand_features(rh)
    pose_feats = extract_pose_features(pose)
    face_feats = extract_face_features(face)
    
    # Concatenate features
    feature_list = []
    
    # Hand features
    feature_list.extend(lh_feats["curls"])
    feature_list.extend(lh_feats["joint_angles"])
    feature_list.extend(lh_feats["pairwise_distances"])
    
    feature_list.extend(rh_feats["curls"])
    feature_list.extend(rh_feats["joint_angles"])
    feature_list.extend(rh_feats["pairwise_distances"])
    
    # Pose features
    feature_list.append(pose_feats["left_elbow_angle"])
    feature_list.append(pose_feats["right_elbow_angle"])
    feature_list.append(pose_feats["shoulder_angle"])
    feature_list.append(pose_feats["arm_extension_left"])
    feature_list.append(pose_feats["arm_extension_right"])
    
    # Face features
    feature_list.append(face_feats["mouth_openness"])
    feature_list.append(face_feats["eyebrow_tilt"])
    
    return np.array(feature_list, dtype=np.float32)
