import os
import pytest

import numpy as np

from ai_engine.landmark_extraction.extractor import landmark_extractor
from app.services.ai_service import ai_service
from app.services.audio_service import audio_service
from app.services.database_service import db_service
from config.config import PROJECT_NAME, SUPPORTED_GESTURES, SUPPORTED_LANGUAGES
from config.logger import setup_logger
from database.mongodb import db_conn


def test_config_loader():
    """Verify that environment config loads correctly with defaults."""
    assert PROJECT_NAME == "SignBridge AI"
    assert "HELLO" in SUPPORTED_GESTURES
    assert "Spanish" in SUPPORTED_LANGUAGES


def test_logger():
    """Verify logger setup functions without errors."""
    logger = setup_logger("test.logger")
    assert logger is not None
    logger.info("Scaffolding test logger message.")


def test_database_connection_offline():
    """Verify db_conn handles connections gracefully."""
    # Should not throw exception even if connection fails or offline
    connected = db_conn.connect()
    # Can be True or False depending on local connection, but should not crash
    assert isinstance(connected, bool)


def test_database_service_fallback():
    """Verify that database operations fallback to local JSON file when offline."""
    # Write a test log
    record = db_service.log_translation(
        detected_gestures=["HELLO", "YES"],
        translated_text="Hello, yes.",
        confidence=0.92,
        language="English",
    )

    assert record is not None
    assert "id" in record
    assert record["translatedText"] == "Hello, yes."

    # Read history
    history = db_service.get_history(limit=5)
    assert len(history) > 0
    assert history[0]["translatedText"] == "Hello, yes."

    # Clean up test entry
    success = db_service.delete_history_record(record["id"])
    assert success is True


def test_landmark_extractor():
    """Verify landmark extractor shapes."""
    # Passing None should output a zero array of shape (1662,)
    vector = landmark_extractor.extract_landmarks(None)
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (1662,)
    assert np.all(vector == 0)


def test_ai_pipeline_mock():
    """Verify inference pipeline processes blank input correctly."""
    # Passing None BGR frame
    results = ai_service.process_frame(None)
    assert results["gesture"] == "IDLE"
    assert results["confidence"] == 0.0


def test_tts_engine_mock():
    """Verify TTS engine generates mock wav files."""
    audio_bytes = audio_service.generate_speech("Test sentence", "en-US")
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 44  # Standard WAV header is 44 bytes


def test_whisper_engine_mock():
    """Verify Whisper engine transcript fallback works."""
    # Mocking standard transcription from a dummy file path
    dummy_filepath = "dummy_audio.wav"
    # Create empty dummy file
    with open(dummy_filepath, "wb") as f:
        f.write(b"WAV DATA")
    try:
        text = audio_service.speech_to_text(dummy_filepath)
        assert len(text) > 0
    finally:
        if os.path.exists(dummy_filepath):
            os.remove(dummy_filepath)


def test_landmark_processor_stub():
    """Verify landmark processor namespace import."""
    from ai_engine.landmark_processor.processor import landmark_processor

    assert landmark_processor is not None


def test_camera_manager_scaffolding():
    """Verify camera manager starts in uninitialized state and closes cleanly."""
    from ai_engine.vision.camera_manager import CameraManager

    cm = CameraManager()
    assert cm.status == "Uninitialized"
    cm.release()


def test_landmark_normalizer():
    """Verify shoulder width relative coordinate scaling."""
    from ai_engine.processing.landmark_normalizer import landmark_normalizer
    from ai_engine.schemas.landmark_schema import (
        FaceTelemetryData,
        FrameLandmarkData,
        HandTelemetryData,
        Point3D,
        PoseTelemetryData,
    )

    # Mock Pose with 33 points (index 11 and 12 are left/right shoulders)
    points = [Point3D(x=0.1, y=0.2, z=0.3, visibility=0.9)] * 33
    points[11] = Point3D(x=0.4, y=0.2, z=0.3, visibility=0.9)  # Left Shoulder
    points[12] = Point3D(x=0.6, y=0.2, z=0.3, visibility=0.9)  # Right Shoulder

    frame = FrameLandmarkData(
        timestamp=1712345678.0,
        left_hand=HandTelemetryData(present=False),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=True, landmarks=points),
        face=FaceTelemetryData(present=False),
    )

    norm = landmark_normalizer.normalize_frame(frame)
    assert norm.pose.present is True
    assert len(norm.pose.landmarks) == 33


def test_temporal_tracker_kinematics():
    """Verify rolling displacements trajectory, direction, and smoothness."""
    from ai_engine.processing.temporal_tracker import TemporalTracker
    from ai_engine.schemas.landmark_schema import (
        FaceTelemetryData,
        FrameLandmarkData,
        HandTelemetryData,
        Point3D,
        PoseTelemetryData,
    )

    tracker = TemporalTracker(history_size=10)
    # Feed sequential movements
    f1 = FrameLandmarkData(
        timestamp=1.0,
        left_hand=HandTelemetryData(present=True, center=Point3D(x=0.0, y=0.0, z=0.0)),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=False),
        face=FaceTelemetryData(present=False),
    )
    f2 = FrameLandmarkData(
        timestamp=2.0,
        left_hand=HandTelemetryData(present=True, center=Point3D(x=0.1, y=0.0, z=0.0)),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=False),
        face=FaceTelemetryData(present=False),
    )
    tracker.update(f1)
    tracker.update(f2)

    metrics = tracker.compute_kinematics("left_hand")
    assert metrics["average_velocity"] > 0.0
    assert metrics["trajectory_length"] == 0.1
    assert metrics["smoothness"] >= 0.0


def test_landmark_recorder_and_session():
    """Verify session creation and coordinates JSON serialization."""
    from ai_engine.schemas.landmark_schema import (
        FaceTelemetryData,
        FrameLandmarkData,
        HandTelemetryData,
        PoseTelemetryData,
    )
    from ai_engine.storage.landmark_recorder import landmark_recorder
    from ai_engine.storage.session_manager import session_manager

    session_id, session_path = session_manager.start_session()
    assert session_id.startswith("session_")

    f = FrameLandmarkData(
        timestamp=1.0,
        left_hand=HandTelemetryData(present=False),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=False),
        face=FaceTelemetryData(present=False),
    )
    landmark_recorder.record_frame(f)
    assert len(landmark_recorder.frame_buffer) == 1

    saved_path = landmark_recorder.save_session("HELLO")
    assert saved_path is not None
    assert saved_path.exists()

    # Cleanup saved file
    saved_path.unlink()
    session_path.rmdir()
    session_manager.end_session()


@pytest.mark.skip(reason="Bypassing PyArrow segmentation fault on Windows")
def test_exporters():
    """Verify CSV, Parquet, and JSON formatting compilation and cleanup."""
    from ai_engine.exporters.csv_exporter import csv_exporter
    from ai_engine.exporters.json_exporter import json_exporter
    from ai_engine.exporters.parquet_exporter import parquet_exporter
    from ai_engine.schemas.landmark_schema import (
        FaceTelemetryData,
        FrameLandmarkData,
        HandTelemetryData,
        PoseTelemetryData,
    )
    from ai_engine.storage.landmark_recorder import landmark_recorder
    from ai_engine.storage.session_manager import session_manager

    session_id, session_path = session_manager.start_session()
    f = FrameLandmarkData(
        timestamp=1.0,
        left_hand=HandTelemetryData(present=False),
        right_hand=HandTelemetryData(present=False),
        pose=PoseTelemetryData(present=False),
        face=FaceTelemetryData(present=False),
    )
    landmark_recorder.record_frame(f)
    saved_path = landmark_recorder.save_session("HELLO")

    json_path = json_exporter.export(saved_path)
    assert json_path is not None
    assert json_path.exists()

    csv_path = csv_exporter.export(saved_path)
    assert csv_path is not None
    assert csv_path.exists()

    parquet_path = parquet_exporter.export(saved_path)
    assert parquet_path is not None
    assert parquet_path.exists()

    # Cleanup exported files
    json_path.unlink()
    csv_path.unlink()
    parquet_path.unlink()

    saved_path.unlink()
    session_path.rmdir()
    session_manager.end_session()


def test_perception_service_quality_readiness():
    """Verify frame brightness, blur score estimation, and readiness coefficient."""
    from ai_engine.services.perception_service import perception_service

    # Generate mock 480x640 frame
    dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

    res = perception_service.process_perception_frame(dummy_frame, 15.0)
    assert res.camera.camera_status is not None
    assert res.readiness.brightness_score == 128.0
    assert res.readiness.frame_quality_score >= 0.0
    assert res.readiness.gesture_readiness >= 0.0
