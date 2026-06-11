import numpy as np

from ai_engine.computer_vision.holistic import MediaPipeHolisticManager
from ai_engine.feature_extractor.extractor import feature_extractor
from ai_engine.inference_preparation.preprocessor import inference_preprocessor
from ai_engine.landmark_extraction.extractor import landmark_extractor
from ai_engine.landmark_processor.processor import landmark_processor
from ai_engine.temporal_memory.memory import temporal_memory
from config.logger import setup_logger

logger = setup_logger("ai_engine.pipeline.vision")

# Fallback import if motion_analyser name differs
try:
    from ai_engine.motion_analysis.analyser import motion_analyser
except ImportError:
    motion_analyser = None


class VisionPipeline:
    def __init__(self):
        self.holistic = MediaPipeHolisticManager()
        self.raw_extractor = landmark_extractor
        self.processor = landmark_processor
        self.feat_extractor = feature_extractor
        self.analyser = motion_analyser
        self.memory = temporal_memory
        self.prep = inference_preprocessor

        # Initialize MediaPipe Holistic
        self.holistic.initialize()

    def run_perception(self, frame_bgr: np.ndarray) -> dict:
        """
        Executes a single cycle of the perception pipeline on the raw image frame.
        Outputs rich coordinate, kinematic, and structural telemetry.
        """
        if frame_bgr is None:
            return {
                "detected": False,
                "tracking_health": 0.0,
                "stability": 1.0,
                "occlusion": 1.0,
                "activity": 0.0,
                "distances": {},
                "angles": {},
                "readiness": {},
                "annotated_frame": None,
            }

        # 1. MediaPipe Processing
        mp_results = self.holistic.process_frame(frame_bgr)

        # 2. Extract Raw landmarks (shape: (1662,))
        raw_coords = self.raw_extractor.extract_landmarks(mp_results)

        # 3. Landmark Processor (Cleaning, Point Recovery, Normalization)
        processed_coords = self.processor.process(raw_coords, mp_results)

        # 4. Feature Extractor (Velocities, Distances, Angles)
        features = self.feat_extractor.extract_all(processed_coords)

        # 5. Motion Analyser (Tremor, Occlusion, Activity, Health)
        motion_telemetry = {}
        if self.analyser is not None:
            motion_telemetry = self.analyser.evaluate(
                processed_coords, features["mean_velocity"], mp_results
            )
        else:
            motion_telemetry = {
                "stability_index": 1.0,
                "occlusion_score": 0.0,
                "activity_index": 0.0,
                "tracking_health": 1.0,
            }

        # 6. Assess AI Readiness
        readiness = self.prep.assess_data_readiness(
            processed_coords, motion_telemetry["tracking_health"]
        )

        # Draw overlays
        annotated_frame = self.holistic.draw_landmarks(frame_bgr, mp_results)

        # Assemble full record
        record = {
            "landmarks": processed_coords.tolist(),
            "mean_velocity": features["mean_velocity"],
            "mean_acceleration": features["mean_acceleration"],
            "distances": features["distances"],
            "angles": features["angles"],
            "stability_index": motion_telemetry["stability_index"],
            "occlusion_score": motion_telemetry["occlusion_score"],
            "activity_index": motion_telemetry["activity_index"],
            "tracking_health": motion_telemetry["tracking_health"],
            "readiness": readiness,
            "annotated_frame": annotated_frame,
            "mp_results": mp_results,
        }

        # 7. Store to rolling buffers
        self.memory.memorize(record)

        return record

    def get_status(self) -> dict:
        return {
            "mediapipe_active": self.holistic._initialized,
            "memory_stats": self.memory.get_memory_stats(),
            "processor_history_length": len(self.processor.history),
            "preprocessor_sequence_length": self.prep.sequence_length,
        }


vision_pipeline = VisionPipeline()
