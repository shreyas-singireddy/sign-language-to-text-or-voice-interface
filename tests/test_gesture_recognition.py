import shutil
import pytest

pytest.importorskip("torch")

import numpy as np
import torch

from ai_engine.gesture_recognition.dataset.sample_validator import sample_validator
from ai_engine.gesture_recognition.features.landmark_features import (
    compile_geometric_features,
    compute_angle,
    unpack_landmarks,
)
from ai_engine.gesture_recognition.features.motion_features import (
    compute_accelerations,
    compute_velocities,
    extract_motion_telemetry,
)
from ai_engine.gesture_recognition.features.temporal_features import (
    compute_trajectory_length,
)
from ai_engine.gesture_recognition.inference.confidence_engine import confidence_engine
from ai_engine.gesture_recognition.inference.post_processor import post_processor
from ai_engine.gesture_recognition.inference.predictor import gesture_predictor
from ai_engine.gesture_recognition.models.alphabet_model import AlphabetMLP
from ai_engine.gesture_recognition.models.word_model import (
    BiLSTMClassifier,
    LSTMClassifier,
    TCNClassifier,
    TransformerClassifier,
)
from ai_engine.gesture_recognition.schemas.prediction_schema import (
    AlphabetPredictionResponse,
    SentencePredictionResponse,
    WordPredictionResponse,
)
from ai_engine.gesture_recognition.storage.checkpoint_manager import CheckpointManager
from ai_engine.gesture_recognition.storage.model_registry import model_registry
from ai_engine.gesture_recognition.training.evaluator import evaluator


# ==========================================
# 1. SCHEMAS & VALIDATORS TESTS
# ==========================================
def test_prediction_schemas():
    """Verify that pydantic schemas validate types correctly."""
    p_alpha = AlphabetPredictionResponse(
        prediction="A", confidence=0.97, alternatives=["S", "E"]
    )
    assert p_alpha.prediction == "A"
    assert len(p_alpha.alternatives) == 2

    p_word = WordPredictionResponse(prediction="HELLO", confidence=0.95)
    assert p_word.prediction == "HELLO"

    p_sent = SentencePredictionResponse(prediction="HELLO YES", confidence=0.92)
    assert p_sent.prediction == "HELLO YES"


def test_sample_validator():
    """Verify landmark validators filter corrupt inputs."""
    valid_vector = np.ones(1662) * 0.5
    is_valid, msg = sample_validator.validate_frame(valid_vector)
    assert is_valid is True

    invalid_shape = np.ones(50)
    is_valid, msg = sample_validator.validate_frame(invalid_shape)
    assert is_valid is False

    nan_vector = np.ones(1662)
    nan_vector[10] = np.nan
    is_valid, msg = sample_validator.validate_frame(nan_vector)
    assert is_valid is False


# ==========================================
# 2. FEATURE ENGINEERING TESTS
# ==========================================
def test_landmark_features():
    """Verify math coordinate conversions and unpacking."""
    dummy_vector = np.ones(1662, dtype=np.float32)
    pose, face, lh, rh = unpack_landmarks(dummy_vector)

    assert pose.shape == (33, 4)
    assert lh.shape == (21, 3)
    assert rh.shape == (21, 3)

    p1 = np.array([1.0, 0.0, 0.0])
    p2 = np.array([0.0, 0.0, 0.0])
    p3 = np.array([0.0, 1.0, 0.0])
    angle = compute_angle(p1, p2, p3)
    assert abs(angle - 90.0) < 1e-4

    geom_feats = compile_geometric_features(dummy_vector)
    assert len(geom_feats) > 0


def test_motion_and_temporal_features():
    """Verify velocity, acceleration, and trajectories."""
    v1 = np.ones(1662)
    v2 = np.ones(1662) * 2
    v3 = np.ones(1662) * 4

    vel = compute_velocities(v2, v1)
    assert np.all(vel == 1.0)

    acc = compute_accelerations(vel, vel * 0)
    assert np.all(acc == 1.0)

    history = [v1, v2, v3]
    mot_telemetry = extract_motion_telemetry(history)
    assert mot_telemetry["left_hand_velocity"] >= 0.0

    traj_l, traj_r = compute_trajectory_length(history)
    assert traj_l >= 0.0


# ==========================================
# 3. MODELS & TRAINING TESTS
# ==========================================
def test_pytorch_models_compile():
    """Verify PyTorch models forward pass and shapes."""
    dummy_inputs = torch.randn(2, 30, 1662)  # Batch 2, Seq 30

    lstm = LSTMClassifier(num_classes=5)
    out = lstm(dummy_inputs)
    assert out.shape == (2, 5)

    bilstm = BiLSTMClassifier(num_classes=5)
    out = bilstm(dummy_inputs)
    assert out.shape == (2, 5)

    transformer = TransformerClassifier(num_classes=5)
    out = transformer(dummy_inputs)
    assert out.shape == (2, 5)

    tcn = TCNClassifier(num_classes=5)
    out = tcn(dummy_inputs)
    assert out.shape == (2, 5)


def test_evaluator_metrics():
    """Verify F1, Accuracy, and confusion matrices calculations."""
    y_true = np.array([0, 1, 2, 0])
    y_pred = np.array([0, 1, 1, 0])
    y_prob = np.array(
        [[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.8, 0.1], [0.9, 0.05, 0.05]]
    )
    classes = ["HELLO", "YES", "NO"]

    metrics = evaluator.evaluate_predictions(y_true, y_pred, y_prob, classes)
    assert metrics["accuracy"] == 0.75
    assert "confusion_matrix" in metrics
    assert len(metrics["class_wise_statistics"]) == 3


# ==========================================
# 4. DATASET & REGISTRY MLOPS TESTS
# ==========================================
def test_model_registry_and_checkpoints(tmp_path):
    """Verify registering, version tags, and checkpoint management."""
    # Instatiate a local registry and manager for tests
    reg = model_registry
    c_mgr = CheckpointManager(tmp_path / "checkpoints")

    model = AlphabetMLP(num_classes=5)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    chk_file = c_mgr.save_checkpoint(model, optimizer, 2, {"loss": 0.1})
    assert chk_file.exists()

    state = c_mgr.load_checkpoint(chk_file, model)
    assert state["epoch"] == 2

    # Register mock model
    dummy_model_path = tmp_path / "dummy.pt"
    torch.save(model.state_dict(), dummy_model_path)

    ver = reg.register_model("word", dummy_model_path, {"acc": 0.9}, ["A", "B"], "LSTM")
    assert ver.startswith("v_word_")

    details = reg.get_active_model_details("word")
    assert details["version"] == ver

    # Cleanup files
    if ver:
        shutil.rmtree(reg.registry_dir / ver, ignore_errors=True)


# ==========================================
# 5. INFERENCE END-TO-END TESTS
# ==========================================
def test_predictor_pipeline_and_confidence():
    """Verify full predictors filtering and post-processing."""
    # Confidence Engine test
    score = confidence_engine.calculate_confidence(
        raw_prob=0.92,
        predicted_label="HELLO",
        tracking_stability=85.0,
        visibility_score=90.0,
    )
    assert score > 50.0

    # Post Processor test
    raw_seq = ["HELLO", "HELLO", "YES", "YES", "IDLE"]
    clean_seq = post_processor.deduplicate_sequence(raw_seq)
    assert clean_seq == ["HELLO", "YES"]

    # Predictor with default fallback model
    dummy_frame = np.ones(1662) * 0.8
    res = gesture_predictor.predict_alphabet(dummy_frame)
    assert "prediction" in res
    assert "confidence" in res
