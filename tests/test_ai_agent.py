import json

import pytest

from ai_engine.ai_agent.error_detection import calculate_angle, error_detector
from ai_engine.ai_agent.learning_coach import learning_coach
from ai_engine.ai_agent.llm_engine import llm_engine
from ai_engine.ai_agent.rag_engine import rag_engine
from ai_engine.schemas.landmark_schema import (
    FaceTelemetryData,
    FrameLandmarkData,
    HandTelemetryData,
    Point3D,
    PoseTelemetryData,
)
from database.learning_schemas import (
    OFFLINE_LEARNING_FILE,
    OFFLINE_QUIZZES_FILE,
    LearningDatabase,
)


def setup_module(module):
    _ = module
    # Clear offline DB files to prevent test state pollution
    if OFFLINE_LEARNING_FILE.exists():
        try:
            OFFLINE_LEARNING_FILE.write_text(json.dumps({}))
        except Exception:
            pass
    if OFFLINE_QUIZZES_FILE.exists():
        try:
            OFFLINE_QUIZZES_FILE.write_text(json.dumps([]))
        except Exception:
            pass


# Mocking coordinate helper
class MockPoint:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z


# --- 1. Test Database Schema & Progress ---
def test_learning_database_get_default():
    db = LearningDatabase()
    progress = db.get_progress("1234567890")
    assert progress["phone"] == "1234567890"
    assert progress["skill_level"] == "Novice"
    assert progress["practice_count"] == 0
    assert progress["average_accuracy"] == 0.0


def test_learning_database_save_and_log():
    db = LearningDatabase()
    phone = "9999999999"

    # Save a baseline progress
    baseline = db.get_progress(phone)
    baseline["streak"] = 2
    db.save_progress(phone, baseline)

    # Log a high accuracy practice
    updated = db.log_practice(phone, 0.90, "HELLO")
    assert updated["practice_count"] == 1
    assert updated["average_accuracy"] == 0.90
    assert "HELLO" not in updated["weak_signs"]

    # Log a low accuracy practice (should add to weak signs)
    updated = db.log_practice(phone, 0.50, "THANK_YOU")
    assert updated["practice_count"] == 2
    assert updated["average_accuracy"] == 0.70  # (0.90 + 0.50) / 2
    assert "THANK_YOU" in updated["weak_signs"]


def test_learning_quiz_save_and_submit():
    db = LearningDatabase()
    phone = "8888888888"
    questions = [{"question_text": "Test Q", "options": ["A", "B"], "correct_answer": "A"}]

    quiz_id = db.save_quiz(phone, questions)
    assert quiz_id.startswith("quiz_")

    success = db.submit_quiz(quiz_id, 100)
    assert success is True


# --- 2. Test LLM Engine Fallbacks ---
def test_llm_engine_fallback():
    # Test that the rule-based mock engine returns appropriate responses when offline
    explanation = llm_engine.generate_completion("explain HELLO sign")
    assert "Sign Explanation" in explanation

    error = llm_engine.generate_completion("detect errors in gesture")
    assert "Postural Alignment Analysis" in error

    quiz = llm_engine.generate_completion("generate quiz questions")
    quiz_json = json.loads(quiz)
    assert len(quiz_json) > 0
    assert "question_text" in quiz_json[0]


# --- 3. Test RAG Search Engine ---
def test_rag_engine_index_and_retrieve():
    # Load and index the documentation
    rag_engine.load_and_index()

    # Query something related to pipeline or database blueprints
    context = rag_engine.retrieve_context("database", top_k=1)
    # RAG should retrieve some text if documentation folder exists
    if rag_engine.chunks:
        assert len(context) > 0
    else:
        assert context == ""


# --- 4. Test Error Detection Computations ---
def test_calculate_angle():
    a = MockPoint(1.0, 0.0, 0.0)
    b = MockPoint(0.0, 0.0, 0.0)  # vertex
    c = MockPoint(0.0, 1.0, 0.0)

    angle = calculate_angle(a, b, c)
    assert pytest.approx(angle, 0.1) == 90.0


def test_error_detection_visible_hand():
    # Create mock frame landmarks
    frame_lms = FrameLandmarkData(
        timestamp=0.0,
        left_hand=HandTelemetryData(present=False, landmarks=[]),
        right_hand=HandTelemetryData(
            present=True, landmarks=[Point3D(x=0.0, y=0.0, z=0.0)] + [Point3D(x=0.5, y=0.5, z=0.5) for _ in range(20)]
        ),
        pose=PoseTelemetryData(
            present=True,
            # Generate 33 landmarks for pose (shoulders, elbows, hip)
            landmarks=[Point3D(x=0.0, y=0.0, z=0.0) for _ in range(33)],
        ),
        face=FaceTelemetryData(present=False, landmarks=[]),
    )

    feedback = error_detector.detect_errors(frame_lms, "HELLO")
    assert "status" in feedback
    assert "overall_accuracy" in feedback
    assert isinstance(feedback["deviations"], list)


# --- 5. Test Learning Coach Quiz & Daily Challenge ---
def test_learning_coach_generators():
    phone = "7777777777"

    # Get daily challenge
    challenge = learning_coach.get_daily_challenge(phone, "English")
    assert "description" in challenge
    assert challenge["target_sign"] == "THANK_YOU"

    # Generate quiz (uses fallback internally if no LLM key)
    quiz_data = learning_coach.generate_quiz(phone, "English", num_questions=2)
    assert "quiz_id" in quiz_data
    assert len(quiz_data["questions"]) > 0
    assert "question_text" in quiz_data["questions"][0]
