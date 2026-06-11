import time
from contextlib import contextmanager

from ai_engine.schemas.telemetry_schema import PerformanceProfilerData


class PerformanceProfiler:
    def __init__(self):
        self.hand_time: float = 0.0
        self.pose_time: float = 0.0
        self.face_time: float = 0.0
        self.detector_time: float = 0.0
        self.pipeline_time: float = 0.0

    @contextmanager
    def time_stage(self, stage_name: str):
        """
        Context manager to time individual pipeline stages in milliseconds.
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000.0
            setattr(self, f"{stage_name}_time", round(elapsed, 2))

    def compile_metrics(self) -> PerformanceProfilerData:
        """
        Assembles all profiled measurements.
        """
        return PerformanceProfilerData(
            detector_latency_ms=self.detector_time,
            hand_inference_ms=self.hand_time,
            pose_inference_ms=self.pose_time,
            face_inference_ms=self.face_time,
            total_pipeline_ms=self.pipeline_time,
        )


performance_profiler = PerformanceProfiler()
