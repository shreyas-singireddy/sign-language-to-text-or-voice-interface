from pathlib import Path

from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RECORDINGS_DIR = BASE_DIR / "data" / "recordings"
EXPORTS_DIR = BASE_DIR / "data" / "exports"

# Ensure dirs exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class CameraSettings(BaseModel):
    source_index: int = Field(default=0, description="Webcam device index")
    width: int = Field(default=640, description="Webcam capture width")
    height: int = Field(default=480, description="Webcam capture height")
    fps_limit: int = Field(default=30, description="Target frame rate cap")


class DetectorSettings(BaseModel):
    min_detection_confidence: float = Field(default=0.5, description="Min detection threshold")
    min_tracking_confidence: float = Field(default=0.5, description="Min tracking threshold")


class TelemetrySettings(BaseModel):
    history_size: int = Field(default=120, description="Temporal tracker history frame count")
    stability_window: int = Field(default=15, description="Jitter calculations window")
    readiness_threshold: int = Field(default=75, description="Gesture readiness percentage check")


class SystemConfig(BaseModel):
    project_name: str = "SignBridge AI Telemetry Engine"
    camera: CameraSettings = CameraSettings()
    detectors: DetectorSettings = DetectorSettings()
    telemetry: TelemetrySettings = TelemetrySettings()
    recordings_path: str = str(RECORDINGS_DIR)
    exports_path: str = str(EXPORTS_DIR)


# Global singleton configuration instance
sys_config = SystemConfig()
