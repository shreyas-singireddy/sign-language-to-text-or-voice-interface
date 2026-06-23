import threading
import time

import numpy as np

from ai_engine.utils.config import sys_config
from ai_engine.utils.cv2_guard import cv2
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("vision.camera")


class CameraManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.cap: cv2.VideoCapture | None = None
        self.camera_index: int = sys_config.camera.source_index
        self.width: int = sys_config.camera.width
        self.height: int = sys_config.camera.height

        # Performance parameters
        self.frame_count: int = 0
        self.fps: float = 0.0
        self.latency_ms: float = 0.0
        self.status: str = "Uninitialized"

        self.prev_time: float = time.time()

    def initialize_camera(self, index: int, width: int = 640, height: int = 480) -> bool:
        """
        Locks thread and starts capture channel on the device index.
        """
        with self.lock:
            self.release()
            self.camera_index = index
            self.width = width
            self.height = height

            logger.info(f"Initializing camera source={index} ({width}x{height})")

            # Use DirectShow on Windows if possible to speed up initialization
            # cv2.CAP_DSHOW can sometimes resolve slow starts
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if os_check() else cv2.VideoCapture(index)

            if not self.cap.isOpened():
                # Fallback to standard index
                self.cap = cv2.VideoCapture(index)

            if not self.cap.isOpened():
                logger.error(f"Failed to open camera index: {index}")
                self.status = "Failed"
                self.cap = None
                return False

            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Set resolution parameters
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # Read a test frame
            success, _ = self.cap.read()
            if not success:
                logger.warning("Camera opened but failed to read initial frame.")
                self.status = "Disconnect/Error"
                return False

            self.status = "Active"
            self.frame_count = 0
            self.prev_time = time.time()
            logger.info(f"Camera index {index} initialized successfully.")
            return True

    def read_frame(self) -> tuple[bool, np.ndarray | None, float]:
        """
        Reads frame, calculates FPS and latency.
        Returns:
            success (bool): capture success
            frame (ndarray): BGR image matrix
            latency_ms (float): elapsed read duration

        BUG-007 FIX: recover_connection() must NOT be called inside the lock
        block — that caused a deadlock because release() also acquires self.lock.
        We now return False from within the lock, and callers can call
        recover_connection() externally if desired.
        """
        t_start = time.time()

        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self.status = "Failed"
                return False, None, 0.0

            success, frame = self.cap.read()

            if not success:
                logger.warning("Frame acquisition failed. Attempting camera recovery...")
                self.status = "Recovery Active"
                # Return False — do NOT call recover_connection() inside the lock
                return False, None, 0.0

            self.frame_count += 1

            # Calculate live FPS
            curr_time = time.time()
            time_diff = curr_time - self.prev_time
            if time_diff >= 1.0:
                self.fps = round(self.frame_count / time_diff, 1)
                self.frame_count = 0
                self.prev_time = curr_time

            self.latency_ms = round((time.time() - t_start) * 1000.0, 2)
            self.status = "Active"
            return True, frame, self.latency_ms

    def recover_connection(self):
        """
        Reinitializes VideoCapture on error or disconnect.
        """
        logger.info(f"Recovering connection to camera index {self.camera_index}...")
        self.release()
        time.sleep(1.0)
        self.initialize_camera(self.camera_index, self.width, self.height)

    def switch_camera(self, index: int) -> bool:
        """
        Changes camera source to new hardware target.
        """
        logger.info(f"Switching camera target to source: {index}")
        return self.initialize_camera(index, self.width, self.height)

    def release(self):
        """
        Releases standard video channels.
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.status = "Released"
            logger.info("Camera resources released.")


# Helper to check platform
def os_check() -> bool:
    import platform

    return platform.system() == "Windows"
