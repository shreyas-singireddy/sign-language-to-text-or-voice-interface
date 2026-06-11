import datetime

from config.logger import setup_logger

logger = setup_logger("communication.hub")


class CommunicationHub:
    def __init__(self):
        self.active_sessions = {}

    def create_session(self, user_id: str) -> str:
        """
        Creates a new interactive sign-language conversation session.
        """
        session_id = f"session_{int(datetime.datetime.now(datetime.UTC).timestamp())}"
        self.active_sessions[session_id] = {
            "creator": user_id,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "messages": [],
            "status": "Active",
        }
        logger.info(f"Created communication session {session_id} for user {user_id}")
        return session_id

    def post_message(
        self, session_id: str, sender: str, text: str, voice_bytes: bytes = None
    ) -> bool:
        """
        Appends a translated sign/message to a session transcript.
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found.")
            return False

        message = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "sender": sender,
            "text": text,
            "has_audio": voice_bytes is not None,
        }
        self.active_sessions[session_id]["messages"].append(message)
        logger.info(f"Message posted in {session_id} by {sender}: '{text}'")
        return True

    def get_session_transcript(self, session_id: str) -> list:
        """
        Retrieves transcript messages for a session.
        """
        if session_id not in self.active_sessions:
            return []
        return self.active_sessions[session_id]["messages"]

    def close_session(self, session_id: str) -> bool:
        """
        Terminates an active session.
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "Closed"
            logger.info(f"Session {session_id} has been closed.")
            return True
        return False


communication_hub = CommunicationHub()
