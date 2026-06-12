from analytics.metrics_collector import metrics_collector
from analytics.report_generator import report_generator


def test_generate_full_report_no_db():
    # Reset collector and register some dummy metrics
    metrics_collector.reset()
    metrics_collector.record_translation(
        signs=["HELLO"],
        translated_text="Hello",
        confidence=0.95,
        elapsed_ms=120,
        language="English",
        emotion="Friendly"
    )

    report = report_generator.generate_full_report()
    assert report["summary"]["total_translations"] == 1
    assert report["summary"]["average_latency_ms"] == 120.0
    assert report["gesture_bar"]["x"] == ["HELLO"]
    assert report["gesture_bar"]["y"] == [1]
    assert report["language_bar"]["x"] == ["English"]
    assert report["language_bar"]["y"] == [1]

def test_generate_full_report_with_db():
    metrics_collector.reset()
    metrics_collector.record_translation(
        signs=["HELLO"],
        translated_text="Hello",
        confidence=0.9,
        elapsed_ms=100,
        language="English",
        emotion="Neutral"
    )

    db_analytics = {
        "gesture_frequency": {"HELLO": 5, "YES": 10},
        "total_translations": 15,
        "average_confidence": 0.85,
        "language_distribution": {"Spanish": 10, "English": 5},
        "daily_activity": {"2026-06-10": 15}
    }

    report = report_generator.generate_full_report(db_analytics)
    assert report["summary"]["total_translations"] == 16  # 15 + 1
    # HELLO frequency: 5 (db) + 1 (live) = 6
    # YES frequency: 10
    g_x = report["gesture_bar"]["x"]
    g_y = report["gesture_bar"]["y"]
    assert "YES" in g_x
    assert "HELLO" in g_x
    assert g_y[g_x.index("HELLO")] == 6
    assert g_y[g_x.index("YES")] == 10

def test_generate_performance_report():
    metrics_collector.reset()
    metrics_collector.record_translation(
        signs=["HELLO"],
        translated_text="Hello",
        confidence=0.9,
        elapsed_ms=100,
        language="English",
        emotion="Neutral"
    )

    perf = report_generator.generate_performance_report()
    assert perf["average_latency_ms"] == 100.0
    assert perf["average_confidence"] == 0.9
    assert perf["total_events"] == 1
