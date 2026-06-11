import json
from pathlib import Path

from ai_engine.schemas.landmark_schema import FrameLandmarkData
from ai_engine.storage.session_manager import session_manager
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("storage.recorder")


class LandmarkRecorder:
    def __init__(self):
        self.frame_buffer: list[dict] = []

    def record_frame(self, frame_data: FrameLandmarkData):
        """
        Serializes and appends the FrameLandmarkData to memory buffer.
        """
        # Convert to dictionary representation for JSON serialization
        self.frame_buffer.append(frame_data.model_dump())

    def save_session(self, label: str) -> Path | None:
        """
        Writes buffered frames to a JSON file on disk.
        """
        session_id, session_path = session_manager.get_active_session()

        if not session_id or not session_path:
            logger.warning("No active session to write to disk.")
            return None

        if not self.frame_buffer:
            logger.warning("Frame buffer is empty. Skipping save.")
            return None

        filepath = session_path / "raw_landmarks.json"

        # Structure dataset sequence meta
        data_packet = {
            "session_id": session_id,
            "label": label.strip().upper(),
            "total_frames": len(self.frame_buffer),
            "frames": self.frame_buffer,
        }

        try:
            with open(filepath, "w") as f:
                json.dump(data_packet, f, indent=4)
            logger.info(f"Recorded landmarks written to disk: {filepath}")

            # Clear buffer after successful save
            self.frame_buffer.clear()
            return filepath
        except Exception as e:
            logger.error(f"Error saving landmark session: {e}")
            return None


landmark_recorder = LandmarkRecorder()
