import json
import tempfile
from pathlib import Path

import numpy as np

from ai_engine.dataset_manager.recorder import DatasetRecorder
from ai_engine.exporters.csv_exporter import CsvExporter
from ai_engine.exporters.json_exporter import JsonExporter
from ai_engine.feature_extractor.extractor import FeatureExtractor
from ai_engine.motion_analysis.analyser import MotionAnalyser
from ai_engine.pipeline.vision_pipeline import vision_pipeline
from ai_engine.temporal_memory.memory import TemporalMemory


def test_temporal_memory():
    mem = TemporalMemory()
    assert mem.get_memory_stats()["buffer_30_size"] == 0

    # Memorize frame
    rec = {
        "landmarks": [0.0] * 1662,
        "mean_velocity": 0.5,
        "mean_acceleration": 0.1,
        "stability_index": 0.9
    }
    mem.memorize(rec)
    stats = mem.get_memory_stats()
    assert stats["buffer_30_size"] == 1
    assert stats["buffer_60_size"] == 1
    assert stats["buffer_120_size"] == 1
    assert stats["is_ready_30"] is False

    mem.clear()
    assert mem.get_memory_stats()["buffer_30_size"] == 0


def test_motion_analyser():
    analyser = MotionAnalyser(buffer_size=5)
    landmarks = np.zeros(1662)

    # stability with < 2 frames
    s1 = analyser.compute_stability_index(landmarks)
    assert s1 == 1.0

    # stability with more frames
    analyser.compute_stability_index(landmarks + 0.1)
    s2 = analyser.compute_stability_index(landmarks - 0.1)
    assert 0.0 <= s2 <= 1.0

    # Activity index scaling
    act = analyser.calculate_activity_index(0.005)
    assert act == 0.5

    # Occlusion score with None results
    occ = analyser.calculate_occlusion_score(None)
    assert occ == 1.0


def test_json_and_csv_exporters():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        raw_session_dir = tmp_path / "session_test123"
        raw_session_dir.mkdir()
        raw_file = raw_session_dir / "raw_landmarks.json"

        # Write dummy raw data
        dummy_data = {
            "label": "HELLO",
            "frames": [
                {
                    "timestamp": 1.0,
                    "left_hand": {
                        "present": True,
                        "landmarks": [{"x": 0.1, "y": 0.2, "z": 0.3, "visibility": 0.9}]
                    },
                    "right_hand": {
                        "present": False,
                        "landmarks": []
                    },
                    "pose": {
                        "present": True,
                        "landmarks": [{"x": 0.4, "y": 0.5, "z": 0.6, "visibility": 0.95}]
                    },
                    "face": {
                        "present": False,
                        "landmarks": []
                    }
                }
            ]
        }

        with open(raw_file, "w") as f:
            json.dump(dummy_data, f)

        # Test JSON Exporter
        j_exp = JsonExporter()
        # Test file missing
        assert j_exp.export(Path("non_existent_file.json")) is None

        # Test successful export
        exported_json = j_exp.export(raw_file)
        assert exported_json is not None
        assert exported_json.exists()

        # Test CSV Exporter
        c_exp = CsvExporter()
        assert c_exp.export(Path("non_existent_file.json")) is None

        exported_csv = c_exp.export(raw_file)
        assert exported_csv is not None
        assert exported_csv.exists()

        # Clean up exported files if they exist in exports folder
        if exported_json and exported_json.exists():
            exported_json.unlink()
        if exported_csv and exported_csv.exists():
            exported_csv.unlink()


def test_dataset_recorder():
    rec = DatasetRecorder()
    assert rec.is_recording is False

    session_id = rec.start_session("THANKS")
    assert session_id.startswith("session_")
    assert rec.is_recording is True
    assert rec.current_label == "THANKS"

    # Capture frame
    success = rec.capture_frame([0.0] * 1662)
    assert success is True
    assert rec.captured_frames_count == 1

    rec.pause_session()
    assert rec.is_recording is False

    success_paused = rec.capture_frame([0.0] * 1662)
    assert success_paused is False

    rec.resume_session()
    assert rec.is_recording is True

    summary = rec.stop_session()
    assert summary["label"] == "THANKS"
    assert summary["frames_count"] == 1

    export_info = rec.export_dataset()
    assert export_info["status"] == "Success"
    assert export_info["total_frames"] == 1


def test_feature_extractor():
    fe = FeatureExtractor()
    landmarks = np.zeros(1662)

    # Test distances
    dists = fe.calculate_distances(landmarks)
    assert dists["lh_thumb_index"] == 0.0

    # Test angles
    angles = fe.calculate_angles(landmarks)
    assert angles["left_elbow_angle"] == 180.0

    # Test velocities
    v, a = fe.calculate_velocities_and_accelerations(landmarks)
    assert np.all(v == 0.0)
    assert np.all(a == 0.0)

    # Second frame to compute velocity
    landmarks_moved = landmarks + 0.1
    v2, a2 = fe.calculate_velocities_and_accelerations(landmarks_moved)
    assert np.allclose(v2, 0.1)
    assert np.allclose(a2, 0.0)

    # Third frame to compute acceleration
    landmarks_moved_more = landmarks_moved + 0.3
    v3, a3 = fe.calculate_velocities_and_accelerations(landmarks_moved_more)
    assert np.allclose(v3, 0.3)
    assert np.allclose(a3, 0.2)



def test_vision_pipeline_none_frame():
    res = vision_pipeline.run_perception(None)
    assert res["detected"] is False
    assert res["tracking_health"] == 0.0


def test_session_replay():
    from unittest import mock

    from ai_engine.replay.session_replay import SessionReplay

    sr = SessionReplay()
    assert sr.load_session(Path("non_existent_file.json")) is False

    # Test generator when no session is loaded
    stream = sr.stream_telemetry()
    assert list(stream) == []

    # Test successful load and stream
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        session_file = tmp_path / "session.json"
        dummy_session = {
            "session_id": "test_id",
            "label": "HELLO",
            "frames": [
                {
                    "timestamp": 1.0,
                    "left_hand": {"present": False},
                    "right_hand": {"present": False},
                    "pose": {"present": False},
                    "face": {"present": False}
                }
            ]
        }
        with open(session_file, "w") as f:
            json.dump(dummy_session, f)

        assert sr.load_session(session_file) is True

        # Test stream telemetry
        with mock.patch("time.sleep", return_value=None):
            telemetry = list(sr.stream_telemetry())
            assert len(telemetry) == 1
            assert telemetry[0].timestamp == 1.0


def test_parquet_exporter():
    from unittest import mock

    from ai_engine.exporters.parquet_exporter import ParquetExporter

    pe = ParquetExporter()
    assert pe.export(Path("non_existent.json")) is None

    # Test fallback to CSV when ImportError is raised (e.g. no pyarrow)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        raw_session_dir = tmp_path / "session_test_parquet"
        raw_session_dir.mkdir()
        raw_file = raw_session_dir / "raw_landmarks.json"

        dummy_data = {
            "label": "HELLO",
            "frames": [
                {
                    "timestamp": 1.0,
                    "left_hand": {"present": False},
                    "right_hand": {"present": False},
                    "pose": {"present": False},
                    "face": {"present": False}
                }
            ]
        }
        with open(raw_file, "w") as f:
            json.dump(dummy_data, f)

        with mock.patch("pandas.DataFrame.to_parquet", side_effect=ImportError):
            exported = pe.export(raw_file)
            assert exported is not None
            # it fell back to CSV, so it should be a CSV file
            assert exported.suffix == ".csv"
            if exported.exists():
                exported.unlink()

