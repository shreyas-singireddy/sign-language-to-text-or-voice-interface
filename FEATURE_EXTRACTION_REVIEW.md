# FEATURE EXTRACTION REVIEW - SignBridge AI Human Perception System

This document details the mathematical formulas, file locations, and example outputs for each feature processed in the pipeline.

---

## 1. Joint Angle Features (Elbows & Shoulders)

*   **Description**: Computes the angle of joint vertices (e.g. shoulder-elbow-wrist).
*   **Formula**:
    $$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right) \cdot \frac{180}{\pi}$$
    Where $\vec{u} = P_1 - P_2$ and $\vec{v} = P_3 - P_2$ (with $P_2$ being the joint vertex).
*   **Implementation File**: [pose_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/pose_detector.py#L51-L66) and [landmark_features.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/features/landmark_features.py#L54-L64)
*   **Output Example**:
    `{"left_elbow_angle": 142.4, "right_elbow_angle": 178.2}`

---

## 2. Finger Curls & Joint Angles

*   **Description**: Measures finger curls and joint angles to classify hand shapes.
*   **Formula**:
    $$\text{Curl}_i = \frac{\|\text{Tip}_i - \text{Wrist}\|}{\|\text{MCP}_i - \text{Wrist}\|}$$
    Joint angles are computed using the cosine rule on the MCP-PIP-DIP landmarks.
*   **Implementation File**: [landmark_features.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/features/landmark_features.py#L66-L124)
*   **Output Example**:
    `{"curls": [1.2, 0.4, 0.3, 0.3, 0.2], "joint_angles": [172.1, 85.4, 78.2, 81.1, 79.4]}`

---

## 3. Pairwise Tip Distances

*   **Description**: Calculates Euclidean distances between all combinations of fingertips (10 combinations total).
*   **Formula**:
    $$d_{ij} = \|\text{Tip}_i - \text{Tip}_j\|_2 = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2 + (z_i - z_j)^2}$$
*   **Implementation File**: [landmark_features.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/gesture_recognition/features/landmark_features.py#L116-L122)
*   **Output Example**:
    `"pairwise_distances": [0.05, 0.12, 0.18, 0.22, 0.08, 0.14, 0.19, 0.07, 0.11, 0.05]`

---

## 4. Velocities & Accelerations

*   **Description**: Measures the change in joint position (displacement) and rate of velocity change (acceleration) between adjacent frames.
*   **Formula**:
    $$\vec{v}_t = \vec{x}_t - \vec{x}_{t-1}$$
    $$\vec{a}_t = \vec{v}_t - \vec{v}_{t-1}$$
*   **Implementation File**: [extractor.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/feature_extractor/extractor.py#L76-L97)
*   **Output Example**:
    `{"mean_velocity": 0.0024, "mean_acceleration": 0.0003}`

---

## 5. Head Orientation Features (Yaw, Pitch, Roll)

*   **Description**: Measures head rotation angles.
*   **Formula**:
    $$\text{Yaw} = 90.0 \cdot (d_{\text{right}} - d_{\text{left}})$$
    $$\text{Pitch} = 120.0 \cdot (y_{\text{nose}} - y_{\text{eyes\_midpoint}} - 0.05)$$
    $$\text{Roll} = \arctan\left(\frac{y_{\text{right\_eye}} - y_{\text{left\_eye}}}{x_{\text{right\_eye}} - x_{\text{left\_eye}}}\right) \cdot \frac{180}{\pi}$$
*   **Implementation File**: [face_detector.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/ai_engine/vision/face_detector.py#L40-L78)
*   **Output Example**:
    `{"head_rotation_pitch": 5.4, "head_rotation_yaw": -12.2, "head_rotation_roll": 2.1}`
