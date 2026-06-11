import datetime
import uuid

from config.logger import setup_logger

logger = setup_logger("ai_engine.dataset_manager")


class DatasetRecorder:
    def __init__(self):
        self.session_id = None
        self.is_recording = False
        self.current_label = None
        self.captured_frames_count = 0
        self.recorded_samples_count = 0
        self.export_status = "Idle"
        self.in_memory_records = []

    def start_session(self, label: str) -> str:
        """
        Starts a dataset recording session.
        """
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.current_label = label.strip().upper()
        self.is_recording = True
        self.captured_frames_count = 0
        self.export_status = "Recording Active"
        self.in_memory_records = []
        logger.info(
            f"Dataset recording session started: ID={self.session_id}, Label={self.current_label}"
        )
        return self.session_id

    def pause_session(self):
        """Pauses recording state."""
        self.is_recording = False
        self.export_status = "Paused"
        logger.info(f"Dataset recording session paused: ID={self.session_id}")

    def resume_session(self):
        """Resumes recording state."""
        self.is_recording = True
        self.export_status = "Recording Active"
        logger.info(f"Dataset recording session resumed: ID={self.session_id}")

    def capture_frame(self, landmark_vector: list) -> bool:
        """
        Buffers a single frame landmark vector if recording is active.
        """
        if not self.is_recording:
            return False

        self.in_memory_records.append(landmark_vector)
        self.captured_frames_count += 1
        return True

    def stop_session(self) -> dict:
        """
        Terminates the capture session and registers the repetition as a completed sample.
        """
        self.is_recording = False
        self.recorded_samples_count += 1
        self.export_status = "Completed Repetition"

        session_summary = {
            "session_id": self.session_id,
            "label": self.current_label,
            "frames_count": self.captured_frames_count,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        logger.info(f"Dataset recording session finished: {session_summary}")
        return session_summary

    def export_dataset(self) -> dict:
        """
        Simulates file conversion exports.
        """
        if not self.session_id:
            return {"status": "Error", "message": "No active session to export."}

        self.export_status = "Exported Successfully"
        export_details = {
            "status": "Success",
            "session_id": self.session_id,
            "label": self.current_label,
            "total_frames": self.captured_frames_count,
            "format": "NumPy Sequence (.npy)",
            "shape": f"(1, {self.captured_frames_count}, 1662)",
            "message": "Vision data compiled and formatted for future training models.",
        }
        logger.info(f"Dataset export completed: {export_details}")
        return export_details


dataset_recorder = DatasetRecorder()
