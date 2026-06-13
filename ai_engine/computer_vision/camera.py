from ai_engine.utils.cv2_guard import cv2

from config.config import WEBCAM_SOURCE
from config.logger import setup_logger

logger = setup_logger("ai_engine.cv.camera")


class CameraManager:
    def __init__(self, source: int = WEBCAM_SOURCE):
        self.source = source
        self.cap = None

    def start(self) -> bool:
        """
        Initializes and starts camera stream.
        """
        if self.cap is not None and self.cap.isOpened():
            return True

        logger.info(f"Opening camera stream source: {self.source}")
        self.cap = cv2.VideoCapture(self.source)

        # Test if camera was successfully opened
        if not self.cap.isOpened():
            logger.error(f"Failed to open video source {self.source}.")
            self.cap = None
            return False

        logger.info("Webcam stream started successfully.")
        return True

    def get_frame(self):
        """
        Reads a frame from the capture stream.
        Returns (success, frame) where frame is BGR array.
        """
        if self.cap is None or not self.cap.isOpened():
            success = self.start()
            if not success:
                return False, None

        success, frame = self.cap.read()
        if not success:
            logger.warning("Failed to retrieve frame from camera.")
        return success, frame

    def stop(self):
        """
        Releases the webcam resources.
        """
        if self.cap is not None:
            logger.info("Releasing camera stream resources.")
            self.cap.release()
            self.cap = None

    def is_running(self) -> bool:
        return self.cap is not None and self.cap.isOpened()
