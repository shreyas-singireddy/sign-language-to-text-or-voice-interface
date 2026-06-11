import numpy as np
from ai_engine.computer_vision.holistic import MediaPipeHolisticManager
from ai_engine.landmark_extraction.extractor import landmark_extractor
from ai_engine.gesture_recognition.detector import gesture_detector
from ai_engine.sequence_models.seq_model import sequence_model
from ai_engine.translation_engine.translator import translation_engine
from config.logger import setup_logger

logger = setup_logger("ai_engine.inference.pipeline")

class InferencePipeline:
    def __init__(self):
        self.holistic_manager = MediaPipeHolisticManager()
        self.extractor = landmark_extractor
        self.detector = gesture_detector
        self.seq_model = sequence_model
        self.translator = translation_engine

        # Initialization
        self.holistic_manager.initialize()

    def run(self, frame_bgr: np.ndarray, language: str = "English") -> dict:
        """
        Executes a complete inference cycle on a single raw video frame.
        """
        if frame_bgr is None:
            return {
                "detected": False,
                "gesture": "IDLE",
                "confidence": 0.0,
                "sequence": [],
                "translation": "",
                "annotated_frame": None
            }

        # 1. MediaPipe Feature Processing
        results = self.holistic_manager.process_frame(frame_bgr)
        hands_detected = self.extractor.has_hands_detected(results)
        
        # 2. Extract Landmarks (flat shape (1662,))
        landmarks = self.extractor.extract_landmarks(results)
        
        # 3. Predict Single Frame Gesture
        gesture, confidence = self.detector.predict(landmarks)
        
        # 4. Feed Sequence Buffer and Decode
        self.seq_model.add_to_buffer(landmarks, gesture)
        gesture_sequence = self.seq_model.decode_sequence()
        
        # 5. Translate Sequence into Sentence
        translation = self.translator.translate(gesture_sequence, language=language)
        
        # 6. Draw Skeleton Overlays
        annotated_frame = self.holistic_manager.draw_landmarks(frame_bgr, results)

        return {
            "hands_detected": hands_detected,
            "landmarks": landmarks.tolist(),
            "gesture": gesture,
            "confidence": round(confidence, 4),
            "sequence": gesture_sequence,
            "translation": translation,
            "annotated_frame": annotated_frame
        }

    def get_status(self) -> dict:
        """Returns diagnostic states of submodules."""
        return {
            "mediapipe_loaded": self.holistic_manager._initialized,
            "detector_model_loaded": self.detector.model_loaded,
            "sequence_model_loaded": self.seq_model.model_loaded,
            "sequence_buffer_size": len(self.seq_model.buffer),
            "supported_gestures_count": len(self.detector.predict.__globals__.get("SUPPORTED_GESTURES", []))
        }

    def reset_sequence(self):
        """Resets the internal prediction history sequence buffer."""
        self.seq_model.clear_buffer()
        logger.info("Inference sequence buffer reset.")

inference_pipeline = InferencePipeline()
