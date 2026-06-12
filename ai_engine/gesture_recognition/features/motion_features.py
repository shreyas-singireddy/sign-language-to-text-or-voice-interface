from typing import Any

import numpy as np


def compute_velocities(current_landmarks: np.ndarray, previous_landmarks: np.ndarray) -> np.ndarray:
    """
    Computes coordinate-wise velocity (displacement) between two frames.
    Input shapes: (1662,)
    """
    if len(current_landmarks) != len(previous_landmarks):
        return np.zeros_like(current_landmarks)
    return current_landmarks - previous_landmarks


def compute_accelerations(current_vel: np.ndarray, previous_vel: np.ndarray) -> np.ndarray:
    """
    Computes coordinate-wise acceleration between consecutive velocity vectors.
    """
    if len(current_vel) != len(previous_vel):
        return np.zeros_like(current_vel)
    return current_vel - previous_vel


def compute_hand_direction(lh_vel: np.ndarray, rh_vel: np.ndarray) -> tuple[float, float]:
    """
    Computes the 2D direction angle (in degrees) of left and right hand centers based on velocity.
    lh_vel and rh_vel are 3D velocity vectors (dx, dy, dz) of the hand centers.
    """
    left_dir = 0.0
    right_dir = 0.0

    if len(lh_vel) >= 2:
        dx, dy = lh_vel[0], lh_vel[1]
        if abs(dx) > 1e-5 or abs(dy) > 1e-5:
            left_dir = float(np.degrees(np.arctan2(dy, dx)))

    if len(rh_vel) >= 2:
        dx, dy = rh_vel[0], rh_vel[1]
        if abs(dx) > 1e-5 or abs(dy) > 1e-5:
            right_dir = float(np.degrees(np.arctan2(dy, dx)))

    return left_dir, right_dir


def extract_motion_telemetry(flat_history: list) -> dict[str, Any]:
    """
    Computes aggregated velocities and accelerations for a sequence history list of flat landmarks.
    """
    metrics = {
        "left_hand_velocity": 0.0,
        "right_hand_velocity": 0.0,
        "left_hand_acceleration": 0.0,
        "right_hand_acceleration": 0.0,
    }

    if len(flat_history) < 2:
        return metrics

    curr = flat_history[-1]
    prev = flat_history[-2]

    # Hand index boundaries
    # Left hand is 1404 to 1467. Right hand is 1467 to 1530.
    lh_curr = curr[1404:1467].reshape((-1, 3))
    lh_prev = prev[1404:1467].reshape((-1, 3))

    rh_curr = curr[1467:1530].reshape((-1, 3))
    rh_prev = prev[1467:1530].reshape((-1, 3))

    # Mean displacement velocity magnitudes
    lh_disps = np.linalg.norm(lh_curr - lh_prev, axis=1)
    metrics["left_hand_velocity"] = float(np.mean(lh_disps))

    rh_disps = np.linalg.norm(rh_curr - rh_prev, axis=1)
    metrics["right_hand_velocity"] = float(np.mean(rh_disps))

    if len(flat_history) >= 3:
        prev_prev = flat_history[-3]
        lh_prev_prev = prev_prev[1404:1467].reshape((-1, 3))
        rh_prev_prev = prev_prev[1467:1530].reshape((-1, 3))

        # Accelerations (difference in displacements)
        lh_disps_prev = np.linalg.norm(lh_prev - lh_prev_prev, axis=1)
        metrics["left_hand_acceleration"] = float(np.mean(np.abs(lh_disps - lh_disps_prev)))

        rh_disps_prev = np.linalg.norm(rh_prev - rh_prev_prev, axis=1)
        metrics["right_hand_acceleration"] = float(np.mean(np.abs(rh_disps - rh_disps_prev)))

    return metrics
