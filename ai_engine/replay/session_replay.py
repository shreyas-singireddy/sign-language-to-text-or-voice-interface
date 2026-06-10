import json
import time
from pathlib import Path
from typing import Generator, Optional, Dict
from ai_engine.utils.logger import get_structured_logger
from ai_engine.schemas.landmark_schema import FrameLandmarkData

logger = get_structured_logger("replay.session")

class SessionReplay:
    def __init__(self):
        self.active_file: Optional[Path] = None
        self.session_data: Optional[dict] = None

    def load_session(self, filepath: Path) -> bool:
        """
        Loads recorded JSON session data.
        """
        if not filepath.exists():
            logger.error(f"Replay file does not exist: {filepath}")
            return False

        try:
            with open(filepath, "r") as f:
                self.session_data = json.load(f)
            self.active_file = filepath
            logger.info(f"Loaded session for replay: ID={self.session_data.get('session_id')}, Label={self.session_data.get('label')}")
            return True
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            return False

    def stream_telemetry(self) -> Generator[FrameLandmarkData, None, None]:
        """
        Simulates and yields coordinates records from the active session.
        """
        if self.session_data is None:
            logger.warning("No active session loaded for replay.")
            return

        frames = self.session_data.get("frames", [])
        logger.info(f"Starting replay stream of {len(frames)} frames...")
        
        for frame in frames:
            # Reconstruct FrameLandmarkData model
            record = FrameLandmarkData(**frame)
            yield record
            # Yield at approx 30 fps (33ms sleep)
            time.sleep(0.033)

session_replay = SessionReplay()
