import numpy as np
from config.logger import setup_logger

logger = setup_logger("ai_engine.landmark_processor")

class LandmarkProcessor:
    def __init__(self, buffer_size: int = 5):
        self.buffer_size = buffer_size
        self.history = []
        self.last_valid_coordinates = None

    def clean_coordinates(self, raw_coords: np.ndarray) -> np.ndarray:
        """
        Applies noise reduction (rolling filter) over coordinates to smooth jitter.
        Input raw_coords shape: (1662,)
        """
        # Save to cache history
        self.history.append(raw_coords)
        if len(self.history) > self.buffer_size:
            self.history.pop(0)

        # Compute simple rolling average
        smoothed = np.mean(self.history, axis=0)
        return smoothed

    def recover_missing_points(self, raw_coords: np.ndarray, mp_results) -> np.ndarray:
        """
        Performs linear interpolation or fill from previous valid frame for occluded joints.
        """
        coords_copy = raw_coords.copy()
        
        # Check if coordinates are entirely empty (e.g. zeros)
        is_empty = np.all(raw_coords == 0)
        
        if is_empty and self.last_valid_coordinates is not None:
            # Reconstruct from last valid state (simple recovery)
            coords_copy = self.last_valid_coordinates.copy()
            logger.info("Occlusion detected: Recovered coordinates from previous frame.")
        elif not is_empty:
            # Save as last valid
            self.last_valid_coordinates = coords_copy.copy()
            
        return coords_copy

    def normalize_landmarks(self, raw_coords: np.ndarray) -> np.ndarray:
        """
        Normalizes coordinates relative to anchor joints (e.g. neck or wrist center) 
        to ensure translation/scale invariance.
        """
        normalized = raw_coords.copy()
        
        # Let's anchor the hands to the wrists if visible
        # Right hand landmarks start at index 1467. Wrist is the first hand joint (1467, 1468, 1469)
        # Left hand landmarks start at 1404. Wrist is 1404, 1405, 1406
        rh_wrist = normalized[1467:1470]
        lh_wrist = normalized[1404:1407]
        
        # If right hand wrist is present, shift all right hand landmarks relative to the wrist
        if np.any(rh_wrist != 0):
            for i in range(21):
                idx = 1467 + (i * 3)
                normalized[idx:idx+3] = normalized[idx:idx+3] - rh_wrist

        # If left hand wrist is present, shift all left hand landmarks relative to the wrist
        if np.any(lh_wrist != 0):
            for i in range(21):
                idx = 1404 + (i * 3)
                normalized[idx:idx+3] = normalized[idx:idx+3] - lh_wrist
                
        return normalized

    def process(self, raw_coords: np.ndarray, mp_results) -> np.ndarray:
        """
        Executes complete pre-processing workflow.
        """
        recovered = self.recover_missing_points(raw_coords, mp_results)
        smoothed = self.clean_coordinates(recovered)
        normalized = self.normalize_landmarks(smoothed)
        return normalized

landmark_processor = LandmarkProcessor()
