import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from ai_engine.gesture_recognition.inference.predictor import gesture_predictor
from ai_engine.gesture_recognition.dataset.gesture_recorder import gesture_recorder
from ai_engine.gesture_recognition.dataset.dataset_manager import dataset_manager
from ai_engine.gesture_recognition.storage.model_registry import model_registry
from ai_engine.gesture_recognition.training.trainer import trainer
from ai_engine.gesture_recognition.training.hyperparameter_tuner import hyperparameter_tuner

class GestureService:
    def __init__(self):
        pass

    def predict_frame(self, 
                      flat_landmarks: np.ndarray, 
                      visibility_score: float = 100.0, 
                      quality_score: float = 100.0, 
                      occlusion_score: float = 0.0, 
                      stability_score: float = 100.0) -> Dict[str, Any]:
        """
        Runs single-frame alphabet prediction.
        """
        return gesture_predictor.predict_alphabet(
            flat_landmarks, visibility_score, quality_score, occlusion_score, stability_score
        )

    def predict_sequence(self, 
                         sequence: List[np.ndarray], 
                         visibility_score: float = 100.0, 
                         quality_score: float = 100.0, 
                         occlusion_score: float = 0.0, 
                         stability_score: float = 100.0) -> Dict[str, Any]:
        """
        Runs temporal sequence word prediction.
        """
        return gesture_predictor.predict_word(
            sequence, visibility_score, quality_score, occlusion_score, stability_score
        )

    def start_recording(self, label: str, user_id: str = "default_user") -> str:
        return gesture_recorder.start_recording(label, user_id)

    def record_frame(self, flat_landmarks: np.ndarray, quality_score: float, visibility_score: float) -> bool:
        return gesture_recorder.record_frame(flat_landmarks, quality_score, visibility_score)

    def stop_and_save_recording(self) -> Optional[Path]:
        return gesture_recorder.stop_and_save_recording()

    def train_gesture_model(self, 
                             model_type: str = "word", 
                             arch_name: str = "LSTM", 
                             epochs: int = 15, 
                             batch_size: int = 16, 
                             lr: float = 0.001) -> Tuple[str, Dict[str, Any]]:
        """
        Triggers training loop.
        """
        return trainer.train_model(
            model_type=model_type,
            arch_name=arch_name,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr
        )

    def tune_model(self, model_type: str = "word", arch_name: str = "LSTM") -> Tuple[Dict[str, Any], float]:
        return hyperparameter_tuner.tune_hyperparameters(model_type, arch_name)

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Exposes registered models and active models details.
        """
        return {
            "active_alphabet": model_registry.get_active_model_details("alphabet"),
            "active_word": model_registry.get_active_model_details("word"),
            "all_models": model_registry.list_models()
        }

    def rollback_model(self, model_type: str, target_version: str) -> bool:
        return model_registry.rollback_model(model_type, target_version)

    def get_dataset_stats(self) -> Dict[str, int]:
        return dataset_manager.get_index().get("labels", {})

    def clear_dataset_label(self, label: str) -> bool:
        """
        Deletes recorded samples from disk and metadata index.
        """
        try:
            # Delete folders
            label_dir = dataset_manager.data_root / label
            if label_dir.exists():
                for f in label_dir.glob("*"):
                    f.unlink()
                label_dir.rmdir()
                
            index = dataset_manager.get_index()
            if label in index.get("labels", {}):
                del index["labels"][label]
                dataset_manager.write_index(index)
            return True
        except Exception:
            return False

gesture_service = GestureService()
