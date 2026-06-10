import cv2
import time
import numpy as np
from ai_engine.utils.logger import get_structured_logger
from ai_engine.vision.camera_manager import CameraManager
from ai_engine.vision.hand_detector import HandDetector
from ai_engine.vision.pose_detector import PoseDetector
from ai_engine.vision.face_detector import FaceDetector
from ai_engine.processing.landmark_normalizer import landmark_normalizer
from ai_engine.processing.temporal_tracker import TemporalTracker
from ai_engine.telemetry.motion_metrics import motion_metrics_calc
from ai_engine.telemetry.stability_metrics import stability_metrics_calc
from ai_engine.telemetry.visibility_metrics import visibility_metrics_calc
from ai_engine.telemetry.occlusion_metrics import occlusion_metrics_calc
from ai_engine.telemetry.performance_metrics import performance_profiler
from ai_engine.schemas.landmark_schema import FrameLandmarkData
from ai_engine.schemas.telemetry_schema import (
    TelemetryResponse, 
    CameraStatusData, 
    StabilityTelemetryData,
    VisibilityTelemetryData, 
    OcclusionTelemetryData, 
    SystemReadinessData,
    PerformanceProfilerData
)

logger = get_structured_logger("services.perception")

class PerceptionService:
    def __init__(self):
        self.camera = CameraManager()
        self.hand_det = HandDetector()
        self.pose_det = PoseDetector()
        self.face_det = FaceDetector()
        self.normalizer = landmark_normalizer
        
        # Build individual trackers for each component
        self.lh_tracker = TemporalTracker()
        self.rh_tracker = TemporalTracker()
        self.pose_tracker = TemporalTracker()
        self.face_tracker = TemporalTracker()

        self.last_frame_time = time.time()

    def process_perception_frame(self, frame: np.ndarray, latency_ms: float) -> TelemetryResponse:
        """
        Runs complete perception pipeline over the input frame and returns Pydantic record.
        """
        t_pipeline_start = time.perf_counter()
        
        # 1. Performance timing of CV parsing
        with performance_profiler.time_stage("detector"):
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            with performance_profiler.time_stage("hand"):
                lh_data, rh_data = self.hand_det.process_frame(frame_rgb)
            with performance_profiler.time_stage("pose"):
                pose_data = self.pose_det.process_frame(frame_rgb)
            with performance_profiler.time_stage("face"):
                face_data = self.face_det.process_frame(frame_rgb)

        # 2. Reconstruct raw FrameLandmarkData
        frame_raw = FrameLandmarkData(
            timestamp=time.time(),
            left_hand=lh_data,
            right_hand=rh_data,
            pose=pose_data,
            face=face_data
        )

        # 3. Landmark Normalization
        frame_normalized = self.normalizer.normalize_frame(frame_raw)

        # 4. Temporal Tracking & Motion calculations
        self.lh_tracker.update(frame_normalized)
        self.rh_tracker.update(frame_normalized)
        self.pose_tracker.update(frame_normalized)
        self.face_tracker.update(frame_normalized)

        lh_kin = self.lh_tracker.compute_kinematics("left_hand")
        rh_kin = self.rh_tracker.compute_kinematics("right_hand")
        pose_kin = self.pose_tracker.compute_kinematics("pose")
        face_kin = self.face_tracker.compute_kinematics("face")

        motion_metrics = motion_metrics_calc.compile_metrics(lh_kin, rh_kin, pose_kin, face_kin)

        # 5. Stability & Quality metrics
        # Flatten raw and smoothed coordinates for jitter check
        raw_lms = self._flatten_landmarks(frame_raw)
        norm_lms = self._flatten_landmarks(frame_normalized)
        stability_metrics = stability_metrics_calc.calculate(raw_lms, norm_lms)

        # 6. Visibility and Occlusion checks
        visibility_metrics = visibility_metrics_calc.calculate(frame_normalized)
        occlusion_metrics = occlusion_metrics_calc.calculate(frame_normalized)

        # 7. Quality & Brightness/Blur checks
        quality_metrics = self._calculate_frame_quality(frame, visibility_metrics, stability_metrics)

        # 8. Compile latency clocks
        performance_profiler.pipeline_time = round((time.perf_counter() - t_pipeline_start) * 1000.0, 2)
        performance_metrics = performance_profiler.compile_metrics()

        # Camera status record
        camera_data = CameraStatusData(
            fps=self.camera.fps,
            latency_ms=latency_ms,
            resolution_width=frame.shape[1],
            resolution_height=frame.shape[0],
            camera_status=self.camera.status,
            frame_count=self.camera.frame_count
        )

        return TelemetryResponse(
            camera=camera_data,
            landmarks=frame_normalized,
            motion=motion_metrics,
            stability=stability_metrics,
            visibility=visibility_metrics,
            occlusion=occlusion_metrics,
            performance=performance_metrics,
            readiness=quality_metrics
        )

    def _flatten_landmarks(self, frame: FrameLandmarkData) -> np.ndarray:
        """Flattens all landmarks into a single numpy vector of size 1662."""
        coords = np.zeros(1662)
        
        # Fill pose
        if frame.pose.present:
            for idx, lm in enumerate(frame.pose.landmarks[:33]):
                offset = idx * 4
                coords[offset:offset+4] = [lm.x, lm.y, lm.z, lm.visibility]
                
        # Fill face
        if frame.face.present:
            for idx, lm in enumerate(frame.face.landmarks[:468]):
                offset = 132 + (idx * 3)
                coords[offset:offset+3] = [lm.x, lm.y, lm.z]
                
        # Fill left hand
        if frame.left_hand.present:
            for idx, lm in enumerate(frame.left_hand.landmarks[:21]):
                offset = 1404 + (idx * 3)
                coords[offset:offset+3] = [lm.x, lm.y, lm.z]
                
        # Fill right hand
        if frame.right_hand.present:
            for idx, lm in enumerate(frame.right_hand.landmarks[:21]):
                offset = 1467 + (idx * 3)
                coords[offset:offset+3] = [lm.x, lm.y, lm.z]
                
        return coords

    def _calculate_frame_quality(self, frame: np.ndarray, vis: VisibilityTelemetryData, stab: StabilityTelemetryData) -> SystemReadinessData:
        """
        Estimates brightness, blur variance, overall frame quality, and gesture readiness scores.
        """
        # Convert BGR to Grayscale for quality calculations
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Brightness (average pixel intensity [0 - 255])
        brightness = float(np.mean(gray))
        
        # Blur (Laplacian variance: larger is sharper)
        blur_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # Brightness Score (ideal is centered between 100 and 190)
        brightness_score = 100.0 - min(100.0, abs(brightness - 145.0) * 0.9)
        
        # Blur Score (ideal is above 100, scale 0 to 100)
        blur_score_scaled = min(100.0, (blur_val / 200.0) * 100.0)
        
        # Combined quality score
        quality = (brightness_score * 0.4) + (blur_score_scaled * 0.4) + (stab.tracking_stability * 0.2)
        
        # Gesture readiness calculations
        # Checks if hands are present and shoulders are visible in pose index 11 and 12
        pose_vis = vis.pose_visibility
        lh_present = vis.left_hand_visibility > 0.5
        rh_present = vis.right_hand_visibility > 0.5
        face_present = vis.face_visibility > 0.5
        
        readiness_score = 0.0
        if face_present: readiness_score += 20.0
        if pose_vis > 0.7: readiness_score += 20.0
        if lh_present: readiness_score += 30.0
        if rh_present: readiness_score += 30.0
        
        # Penalize if blur is high
        if blur_val < 50.0:
            readiness_score *= 0.5

        return SystemReadinessData(
            frame_quality_score=round(quality, 2),
            blur_score=round(blur_val, 2),
            brightness_score=round(brightness, 2),
            gesture_readiness=round(readiness_score, 2)
        )

    def close(self):
        self.camera.release()
        self.hand_det.close()
        self.pose_det.close()
        self.face_det.close()

# Singleton service accessor
perception_service = PerceptionService()
