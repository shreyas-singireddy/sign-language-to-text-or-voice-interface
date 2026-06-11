import os
import json
import numpy as np
from pathlib import Path
from config.config import DATASETS_DIR
from config.logger import setup_logger

logger = setup_logger("ai_engine.datasets")

class DatasetManager:
    def __init__(self, data_dir: Path = DATASETS_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.data_dir / "dataset_index.json"
        self._initialize_index()

    def _initialize_index(self):
        if not self.index_file.exists():
            with open(self.index_file, "w") as f:
                json.dump({}, f)

    def _read_index(self) -> dict:
        try:
            with open(self.index_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_index(self, index: dict):
        try:
            with open(self.index_file, "w") as f:
                json.dump(index, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write dataset index: {e}")

    def save_sample(self, label: str, landmarks: list) -> bool:
        """
        Saves a single frame landmark vector to disk under the respective label.
        """
        try:
            label_dir = self.data_dir / label
            label_dir.mkdir(exist_ok=True)
            
            # Read index to get the count
            index = self._read_index()
            count = index.get(label, 0)
            
            # Save landmark array
            filename = f"sample_{count}.npy"
            filepath = label_dir / filename
            np.save(str(filepath), np.array(landmarks))
            
            # Update index
            index[label] = count + 1
            self._write_index(index)
            
            logger.info(f"Saved training sample for label '{label}' at {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save landmark sample: {e}")
            return False

    def get_statistics(self) -> dict:
        """
        Returns number of samples collected per label.
        """
        index = self._read_index()
        # Ensure count matches actual filesystem files
        stats = {}
        for label in index.keys():
            label_dir = self.data_dir / label
            if label_dir.exists():
                npy_files = list(label_dir.glob("*.npy"))
                stats[label] = len(npy_files)
            else:
                stats[label] = 0
        return stats

    def clear_label(self, label: str) -> bool:
        """
        Deletes all recorded samples for a specific label.
        """
        try:
            label_dir = self.data_dir / label
            if label_dir.exists():
                for f in label_dir.glob("*.npy"):
                    f.unlink()
                label_dir.rmdir()
            
            index = self._read_index()
            if label in index:
                del index[label]
                self._write_index(index)
            
            logger.info(f"Cleared all dataset samples for label '{label}'")
            return True
        except Exception as e:
            logger.error(f"Failed to clear label samples: {e}")
            return False

dataset_manager = DatasetManager()
