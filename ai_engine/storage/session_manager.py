import datetime
from pathlib import Path

from ai_engine.utils.config import sys_config
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("storage.sessions")


class SessionManager:
    def __init__(self):
        self.active_session_id: str | None = None
        self.active_session_path: Path | None = None

    def start_session(self) -> tuple[str, Path]:
        """
        Creates a new session folder.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.active_session_id = f"session_{timestamp}"

        # Create folder under recordings
        self.active_session_path = (
            Path(sys_config.recordings_path) / self.active_session_id
        )
        self.active_session_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Session started: ID={self.active_session_id}")
        return self.active_session_id, self.active_session_path

    def get_active_session(self) -> tuple[str | None, Path | None]:
        return self.active_session_id, self.active_session_path

    def end_session(self):
        logger.info(f"Session ended: ID={self.active_session_id}")
        self.active_session_id = None
        self.active_session_path = None


session_manager = SessionManager()
