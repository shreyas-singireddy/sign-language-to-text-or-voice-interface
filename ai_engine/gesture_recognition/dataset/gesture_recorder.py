import time
import json
import uuid
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.config import DATASETS_DIR
from ai_engine.gesture_recognition.dataset.dataset_manager import dataset_manager
from ai_engine.gesture_recognition.dataset.sample_validator import sample_validator

class GestureRecorder:
    def __init__(self, output_dir: Path = DATASETS_DIR):
        self.output_dir = Path(output_dir)
        self.active_recording = False
        self.current_label = ""
        self.current_user_id = "default_user"
        self.current_session_id = ""
        self.frame_buffer: List[np.ndarray] = []
        self.quality_scores: List[float] = []
        self.visibility_scores: List[float] = []

    def start_recording(self, label: str, user_id: str = "default_user") -> str:
        """
        Starts a new recording session.
        """
        self.active_recording = True
        self.current_label = label.strip().upper()
        self.current_user_id = user_id
        self.current_session_id = f"rec_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        self.frame_buffer.clear()
        self.quality_scores.clear()
        self.visibility_scores.clear()
        return self.current_session_id

    def record_frame(self, flat_landmarks: np.ndarray, quality_score: float, visibility_score: float) -> bool:
        """
        Appends a frame of landmarks to the session buffer.
        """
        if not self.active_recording:
            return False
            
        # Run frame validation check
        is_valid, _ = sample_validator.validate_frame(flat_landmarks)
        if not is_valid:
            return False

        self.frame_buffer.append(flat_landmarks.copy())
        self.quality_scores.append(quality_score)
        self.visibility_scores.append(visibility_score)
        return True

    def stop_and_save_recording(self) -> Optional[Path]:
        """
        Stops session and writes accumulated coordinates to disk.
        """
        if not self.active_recording:
            return None

        self.active_recording = False
        
        if not self.frame_buffer:
            return None
            
        # Verify sequence length and visibility limits
        is_valid, err_msg = sample_validator.validate_sequence(self.frame_buffer)
        if not is_valid:
            # Clear buffer and reject
            self.frame_buffer.clear()
            return None

        # Build folder for label
        label_dir = self.output_dir / self.current_label
        label_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine sequence index
        index = dataset_manager.get_index()
        count = index.get("labels", {}).get(self.current_label, 0)
        
        # File paths
        filename = f"sample_{self.current_session_id}_{count}"
        npy_path = label_dir / f"{filename}.npy"
        meta_path = label_dir / f"{filename}_meta.json"
        
        try:
            # Save raw landmark matrix
            np.save(str(npy_path), np.array(self.frame_buffer, dtype=np.float32))
            
            # Save metadata
            meta = {
                "session_id": self.current_session_id,
                "user_id": self.current_user_id,
                "label": self.current_label,
                "timestamp": time.time(),
                "frame_count": len(self.frame_buffer),
                "average_quality_score": float(np.mean(self.quality_scores)) if self.quality_scores else 100.0,
                "average_visibility_score": float(np.mean(self.visibility_scores)) if self.visibility_scores else 100.0,
            }
            
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=4)
                
            # Update index
            labels_index = index.get("labels", {})
            labels_index[self.current_label] = count + 1
            index["labels"] = labels_index
            dataset_manager.write_index(index)
            
            return npy_path
        except Exception:
            return None
        finally:
            self.frame_buffer.clear()

gesture_recorder = GestureRecorder()
