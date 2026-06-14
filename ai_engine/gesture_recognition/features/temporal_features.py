import numpy as np


def compute_trajectory_length(sequence_history: list) -> tuple[float, float]:
    """
    Computes cumulative trajectory path length for left and right hand centers.
    Input: list of flat arrays (seq_len, 1662)
    Returns:
        left_path_length, right_path_length
    """
    if len(sequence_history) < 2:
        return 0.0, 0.0

    left_path = 0.0
    right_path = 0.0

    # Extract hand centers at each frame
    # Left hand is 1536:1599, right is 1599:1662
    lh_centers = []
    rh_centers = []

    for frame in sequence_history:
        lh = frame[1536:1599].reshape((21, 3))
        rh = frame[1599:1662].reshape((21, 3))

        # Avoid zero/uninitialized hand coords
        if np.any(lh > 0.0):
            lh_centers.append(np.mean(lh, axis=0))
        if np.any(rh > 0.0):
            rh_centers.append(np.mean(rh, axis=0))

    # Accumulate distances
    for i in range(1, len(lh_centers)):
        left_path += float(np.linalg.norm(lh_centers[i] - lh_centers[i - 1]))

    for i in range(1, len(rh_centers)):
        right_path += float(np.linalg.norm(rh_centers[i] - rh_centers[i - 1]))

    return left_path, right_path


def compute_rolling_summary(sequence_history: list) -> dict[str, np.ndarray]:
    """
    Computes temporal descriptors (mean and standard deviation) for all coordinates
    over the sequence window.
    """
    if not sequence_history:
        return {"mean": np.zeros(1662), "std": np.zeros(1662)}

    seq_arr = np.array(sequence_history)  # shape: (seq_len, 1662)
    mean = np.mean(seq_arr, axis=0)
    std = np.std(seq_arr, axis=0)

    return {"mean": mean, "std": std}


def get_gesture_duration(sequence_history: list, fps: float = 25.0) -> float:
    """
    Estimates the duration of the gesture sequence in seconds.
    """
    return len(sequence_history) / fps
