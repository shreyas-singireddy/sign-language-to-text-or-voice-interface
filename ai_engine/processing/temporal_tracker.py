import collections
import numpy as np
from typing import List, Dict
from ai_engine.utils.config import sys_config
from ai_engine.schemas.landmark_schema import Point3D, FrameLandmarkData

class TemporalTracker:
    def __init__(self, history_size: int = sys_config.telemetry.history_size):
        self.history_size = history_size
        self.frame_history = collections.deque(maxlen=history_size)

    def update(self, frame_data: FrameLandmarkData):
        """
        Appends frame data to historical logs.
        """
        self.frame_history.append(frame_data)

    def compute_kinematics(self, component_name: str) -> dict:
        """
        Calculates: velocity, acceleration, trajectory, direction, smoothness, entropy.
        component_name: "left_hand", "right_hand", "pose", "face"
        """
        history_len = len(self.frame_history)
        if history_len < 2:
            return {
                "average_velocity": 0.0,
                "peak_velocity": 0.0,
                "movement_direction": 0.0,
                "motion_energy": 0.0,
                "trajectory_length": 0.0,
                "smoothness": 100.0,
                "motion_entropy": 0.0
            }

        # Extract coordinate centers / nose values over time to compute metrics
        speeds = []
        accelerations = []
        positions = []

        for frame in self.frame_history:
            comp = getattr(frame, component_name)
            if not comp.present:
                continue
                
            # Determine representative point: Center for hands/face, nose (idx 0) for pose
            if component_name in ("left_hand", "right_hand"):
                ref = np.array([comp.center.x, comp.center.y, comp.center.z])
            elif component_name == "pose" and len(comp.landmarks) > 0:
                ref = np.array([comp.landmarks[0].x, comp.landmarks[0].y, comp.landmarks[0].z])
            elif component_name == "face" and len(comp.landmarks) > 0:
                ref = np.array([comp.landmarks[1].x, comp.landmarks[1].y, comp.landmarks[1].z]) # Nose bridge
            else:
                continue
            positions.append(ref)

        if len(positions) < 2:
            return {
                "average_velocity": 0.0,
                "peak_velocity": 0.0,
                "movement_direction": 0.0,
                "motion_energy": 0.0,
                "trajectory_length": 0.0,
                "smoothness": 100.0,
                "motion_entropy": 0.0
            }

        # Displacements (Velocity)
        trajectory_len = 0.0
        directions = []
        for i in range(1, len(positions)):
            disp = positions[i] - positions[i-1]
            dist = np.linalg.norm(disp)
            speeds.append(dist)
            trajectory_len += dist
            
            # Direction angle in XY plane
            if dist > 1e-5:
                angle = np.degrees(np.arctan2(disp[1], disp[0]))
                directions.append(angle)

        # Accelerations
        for i in range(1, len(speeds)):
            acc = abs(speeds[i] - speeds[i-1])
            accelerations.append(acc)

        avg_vel = float(np.mean(speeds)) if speeds else 0.0
        peak_vel = float(np.max(speeds)) if speeds else 0.0
        avg_dir = float(np.mean(directions)) if directions else 0.0
        motion_energy = float(np.mean(np.square(speeds))) if speeds else 0.0

        # Smoothness: Inverse of acceleration variance
        acc_var = np.var(accelerations) if accelerations else 0.0
        smoothness = float(100.0 / (1.0 + (acc_var * 100.0)))

        # Motion Entropy: Shannon entropy of velocity distribution
        entropy = 0.0
        if speeds and len(speeds) > 5:
            hist, _ = np.histogram(speeds, bins=10, density=True)
            hist = hist[hist > 0]
            entropy = float(-np.sum(hist * np.log2(hist)))

        return {
            "average_velocity": round(avg_vel, 4),
            "peak_velocity": round(peak_vel, 4),
            "movement_direction": round(avg_dir, 2),
            "motion_energy": round(motion_energy, 4),
            "trajectory_length": round(trajectory_len, 4),
            "smoothness": round(smoothness, 2),
            "motion_entropy": round(entropy, 3)
        }
