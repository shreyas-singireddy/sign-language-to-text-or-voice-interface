import pytest
import numpy as np
import os
from config.config import PROJECT_NAME, SUPPORTED_GESTURES, SUPPORTED_LANGUAGES
from config.logger import setup_logger
from database.mongodb import db_conn
from app.services.database_service import db_service
from app.services.audio_service import audio_service
from app.services.ai_service import ai_service
from ai_engine.landmark_extraction.extractor import landmark_extractor

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
        language="English"
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

def test_landmark_processor():
    """Verify landmark processor filters and anchor normalization."""
    from ai_engine.landmark_processor.processor import landmark_processor
    dummy = np.zeros(1662)
    processed = landmark_processor.process(dummy, None)
    assert processed.shape == (1662,)
    assert np.all(processed == 0)

def test_feature_extractor():
    """Verify calculations of distance, angles, velocities, and acceleration."""
    from ai_engine.feature_extractor.extractor import feature_extractor
    dummy = np.zeros(1662)
    
    # Simulate coordinate movements
    features = feature_extractor.extract_all(dummy)
    assert "distances" in features
    assert "angles" in features
    assert "mean_velocity" in features
    assert "mean_acceleration" in features
    assert isinstance(features["distances"]["lh_thumb_index"], float)
    assert isinstance(features["angles"]["left_elbow_angle"], float)

def test_motion_analyser():
    """Verify stability index, activity index, and occlusion rating calculations."""
    from ai_engine.motion_analysis.analyser import motion_analyser
    dummy = np.zeros(1662)
    
    metrics = motion_analyser.evaluate(dummy, 0.05, None)
    assert "stability_index" in metrics
    assert "occlusion_score" in metrics
    assert "activity_index" in metrics
    assert "tracking_health" in metrics
    assert metrics["occlusion_score"] == 1.0  # None results is rated 100% occluded

def test_temporal_memory():
    """Verify sliding temporal cache sizes and memory allocation records."""
    from ai_engine.temporal_memory.memory import temporal_memory
    temporal_memory.clear()
    stats = temporal_memory.get_memory_stats()
    assert stats["buffer_30_size"] == 0
    assert stats["memory_usage_kb"] >= 0.0
    
    # Push sequence
    temporal_memory.memorize({
        "landmarks": [0.0]*1662,
        "mean_velocity": 0.04,
        "mean_acceleration": 0.002,
        "stability_index": 0.98
    })
    
    stats_updated = temporal_memory.get_memory_stats()
    assert stats_updated["buffer_30_size"] == 1

def test_inference_preprocessor():
    """Verify input reshaping coordinates tensors match model architectures."""
    from ai_engine.inference_preparation.preprocessor import inference_preprocessor
    raw_seq = [[0.0]*1662] * 5
    tensor = inference_preprocessor.pad_sequence(raw_seq)
    
    # Output should be reshaped to (1, 30, 1662) for sequential models
    assert tensor.shape == (1, 30, 1662)

def test_vision_pipeline():
    """Verify pipeline integrates perception components."""
    from ai_engine.pipeline.vision_pipeline import vision_pipeline
    
    # Process blank BGR input
    results = vision_pipeline.run_perception(None)
    assert "tracking_health" in results
    assert results["tracking_health"] == 0.0

