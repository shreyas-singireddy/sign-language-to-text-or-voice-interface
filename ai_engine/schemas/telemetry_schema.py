from pydantic import BaseModel, Field

from ai_engine.schemas.landmark_schema import FrameLandmarkData


class CameraStatusData(BaseModel):
    fps: float = Field(..., description="Active frames rate")
    latency_ms: float = Field(..., description="Capture processing latency")
    resolution_width: int = Field(..., description="Frame pixel width")
    resolution_height: int = Field(..., description="Frame pixel height")
    camera_status: str = Field(..., description="Camera state status")
    frame_count: int = Field(default=0, description="Cumulative frames read")


class MotionTelemetryData(BaseModel):
    average_velocity: float = Field(..., description="Mean speed magnitude")
    peak_velocity: float = Field(..., description="Highest speed recorded")
    movement_direction: float = Field(..., description="Direction angle yaw")
    motion_energy: float = Field(..., description="Kinetic motion energy index")
    trajectory_length: float = Field(default=0.0, description="Sum distance travelled")
    smoothness: float = Field(default=100.0, description="Acceleration smoothness rating")
    motion_entropy: float = Field(default=0.0, description="Kinetic complexity index")


class ComponentMotionMetrics(BaseModel):
    left_hand: MotionTelemetryData = Field(..., description="Left Hand velocities")
    right_hand: MotionTelemetryData = Field(..., description="Right Hand velocities")
    pose: MotionTelemetryData = Field(..., description="Pose velocities")
    face: MotionTelemetryData = Field(..., description="Face mesh movement")


class StabilityTelemetryData(BaseModel):
    tracking_stability: float = Field(..., description="Telemetry stability score [0-100]")
    landmark_jitter: float = Field(..., description="Jitter variation index")
    frame_consistency: float = Field(..., description="Frame-to-frame similarity rate")


class VisibilityTelemetryData(BaseModel):
    left_hand_visibility: float = Field(..., description="Left hand presence ratio")
    right_hand_visibility: float = Field(..., description="Right hand presence ratio")
    face_visibility: float = Field(..., description="Face keypoints ratio")
    pose_visibility: float = Field(..., description="Pose points visibility")
    overall_visibility: float = Field(..., description="System visibility score [0-100]")


class OcclusionTelemetryData(BaseModel):
    occlusion_percentage: float = Field(..., description="Points occluded percentage")
    tracking_loss_percentage: float = Field(..., description="Tracking loss rate")
    hand_outside_frame: bool = Field(default=False, description="Hand boundaries check")
    partial_face: bool = Field(default=False, description="Partial face detection status")
    missing_landmarks: bool = Field(default=False, description="Occluded segments flag")
    body_cutoff: bool = Field(default=False, description="Pose cutoff check")


class PerformanceProfilerData(BaseModel):
    detector_latency_ms: float = Field(..., description="Overall detectors parse time")
    hand_inference_ms: float = Field(..., description="MediaPipe Hands evaluation time")
    pose_inference_ms: float = Field(..., description="MediaPipe Pose evaluation time")
    face_inference_ms: float = Field(..., description="MediaPipe Face Mesh evaluation time")
    total_pipeline_ms: float = Field(..., description="Complete execution cycle time")


class SystemReadinessData(BaseModel):
    frame_quality_score: float = Field(..., description="Brightness and blur grade [0-100]")
    blur_score: float = Field(..., description="Image blur variance")
    brightness_score: float = Field(..., description="Average pixel intensity")
    gesture_readiness: float = Field(..., description="Ready threshold index [0-100]")


class TelemetryResponse(BaseModel):
    camera: CameraStatusData = Field(..., description="Webcam specifications")
    landmarks: FrameLandmarkData = Field(..., description="Current frame raw coordinates")
    motion: ComponentMotionMetrics = Field(..., description="Kinematics speeds")
    stability: StabilityTelemetryData = Field(..., description="Noise control telemetry")
    visibility: VisibilityTelemetryData = Field(..., description="Joint visibility indexes")
    occlusion: OcclusionTelemetryData = Field(..., description="Body cutoff parameters")
    performance: PerformanceProfilerData = Field(..., description="Execution profiler clocks")
    readiness: SystemReadinessData = Field(..., description="Quality checks")
