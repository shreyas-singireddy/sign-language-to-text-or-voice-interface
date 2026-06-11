import numpy as np

from ai_engine.datasets.dataset_manager import dataset_manager
from ai_engine.inference.pipeline import inference_pipeline
from config.logger import setup_logger

logger = setup_logger("services.ai")


class AIService:
    def __init__(self):
        self.pipeline = inference_pipeline
        self.datasets = dataset_manager

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Runs the full AI pipeline on a single frame.
        Flow: frame -> landmarks -> gesture -> translation
        """
        return self.pipeline.run(frame)

    def get_pipeline_status(self) -> dict:
        """
        Returns active statuses of computer vision modules.
        """
        return self.pipeline.get_status()

    def record_sample(self, label: str, landmarks: list) -> bool:
        """
        Saves landmark features under a specific gesture label.
        """
        logger.info(f"Recording training sample for label: {label}")
        return self.datasets.save_sample(label, landmarks)

    def get_dataset_stats(self) -> dict:
        """
        Summarizes captured dataset counts.
        """
        return self.datasets.get_statistics()

    def clear_dataset_label(self, label: str) -> bool:
        """
        Deletes samples for a specific label.
        """
        return self.datasets.clear_label(label)


ai_service = AIService()
