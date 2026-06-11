from pydantic import BaseModel, Field


class Point3D(BaseModel):
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    visibility: float = Field(default=1.0, description="Confidence/visibility score")


class BoundingBox3D(BaseModel):
    min_point: Point3D = Field(..., description="Min bounding bounds")
    max_point: Point3D = Field(..., description="Max bounding bounds")


class HandTelemetryData(BaseModel):
    present: bool = Field(..., description="Whether hand is in frame")
    landmarks: list[Point3D] = Field(
        default_factory=list, description="21 landmarks list"
    )
    confidence: float = Field(default=0.0, description="MediaPipe confidence")
    center: Point3D = Field(
        default_factory=lambda: Point3D(x=0, y=0, z=0),
        description="Geometric center point",
    )
    bounding_box: BoundingBox3D | None = Field(
        default=None, description="3D Bounding bounds"
    )


class PoseTelemetryData(BaseModel):
    present: bool = Field(..., description="Whether pose is in frame")
    landmarks: list[Point3D] = Field(
        default_factory=list, description="33 keypoints list"
    )
    confidence: float = Field(default=0.0, description="MediaPipe confidence")
    left_arm_angle: float = Field(default=180.0, description="Left arm elbow degrees")
    right_arm_angle: float = Field(default=180.0, description="Right arm elbow degrees")
    shoulder_angle: float = Field(default=0.0, description="Alignment shoulders angle")
    torso_rotation: float = Field(
        default=0.0, description="Body alignment projection angle"
    )


class FaceTelemetryData(BaseModel):
    present: bool = Field(..., description="Whether face is in frame")
    landmarks: list[Point3D] = Field(
        default_factory=list, description="Mesh landmarks list"
    )
    confidence: float = Field(default=0.0, description="MediaPipe confidence")
    mouth_openness: float = Field(default=0.0, description="Mouth opening ratio")
    head_rotation_pitch: float = Field(default=0.0, description="Tilt vertical degree")
    head_rotation_yaw: float = Field(default=0.0, description="Tilt horizontal degree")
    head_rotation_roll: float = Field(default=0.0, description="Tilt rotational degree")
    visibility: float = Field(default=0.0, description="Face visibility ratio")


class FrameLandmarkData(BaseModel):
    timestamp: float = Field(..., description="Unix epoch timestamp")
    left_hand: HandTelemetryData = Field(..., description="Left Hand metrics")
    right_hand: HandTelemetryData = Field(..., description="Right Hand metrics")
    pose: PoseTelemetryData = Field(..., description="Pose/Upper skeleton metrics")
    face: FaceTelemetryData = Field(..., description="Face keypoints metrics")
