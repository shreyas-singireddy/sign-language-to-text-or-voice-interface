import numpy as np


class SampleValidator:
    def __init__(
        self,
        min_sequence_len: int = 10,
        max_sequence_len: int = 120,
        min_visibility: float = 0.3,
    ):
        self.min_sequence_len = min_sequence_len
        self.max_sequence_len = max_sequence_len
        self.min_visibility = min_visibility

    def validate_frame(self, flat_landmarks: np.ndarray | list[float]) -> tuple[bool, str]:
        """
        Validates structure and value range of a single-frame flat landmark vector.
        """
        arr = np.array(flat_landmarks)

        # Check size
        if arr.shape != (1662,):
            return False, f"Invalid shape: expected (1662,), got {arr.shape}"

        # Check for NaN / Inf values
        if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
            return False, "Data contains NaN or infinite values"

        # Check basic coordinate boundaries (usually normalized between -5.0 and 5.0)
        if np.any(np.abs(arr) > 100.0):
            return False, "Coordinate values out of standard bounding range"

        return True, "Valid frame data"

    def validate_sequence(self, sequence: list[np.ndarray], min_vis_ratio: float = 0.5) -> tuple[bool, str]:
        """
        Validates a temporal sequence of frame landmark vectors.
        """
        # Validate sequence length
        seq_len = len(sequence)
        if seq_len < self.min_sequence_len:
            return (
                False,
                f"Sequence too short: got {seq_len} frames, min is {self.min_sequence_len}",
            )
        if seq_len > self.max_sequence_len:
            return (
                False,
                f"Sequence too long: got {seq_len} frames, max is {self.max_sequence_len}",
            )

        # Validate each frame in sequence
        for i, frame in enumerate(sequence):
            is_valid, err_msg = self.validate_frame(frame)
            if not is_valid:
                return False, f"Frame {i} failed validation: {err_msg}"

        # Check visibility profile
        # Pose visibility column is at index 3, 7, 11, etc. in first 132 elements
        visible_frames = 0
        for frame in sequence:
            pose_visibilities = frame[3:132:4]
            mean_vis = np.mean(pose_visibilities) if len(pose_visibilities) > 0 else 0.0
            if mean_vis >= self.min_visibility:
                visible_frames += 1

        if (visible_frames / seq_len) < min_vis_ratio:
            return (
                False,
                f"Visibility tracking is too poor: only {visible_frames}/{seq_len} frames are visible",
            )

        return True, "Sequence matches required training quality parameters"


sample_validator = SampleValidator()
