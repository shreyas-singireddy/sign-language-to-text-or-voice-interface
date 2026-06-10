"""
SignBridge AI — Layer 9: Report Generator
Generates chart-ready data objects for the Analytics Dashboard.
Combines MetricsCollector data, database records, and heatmap builder
into display-ready Plotly figure configurations.
"""
from typing import Dict, List, Any, Optional
from analytics.metrics_collector import metrics_collector
from analytics.heatmap_builder import heatmap_builder
from config.logger import setup_logger

logger = setup_logger("analytics.report_generator")


class ReportGenerator:
    """
    Aggregates analytics data from MetricsCollector and DatabaseService
    into Plotly-compatible chart configurations for the dashboard.
    """

    def generate_full_report(self, db_analytics: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a complete analytics report combining live session metrics
        and database historical data.

        Args:
            db_analytics: Optional analytics dict from DatabaseService.get_analytics()

        Returns:
            Full report dict with all chart configurations
        """
        live = metrics_collector.get_full_metrics_snapshot()

        # Merge with database analytics if provided
        if db_analytics:
            merged_gesture_freq = {**db_analytics.get("gesture_frequency", {})}
            for gesture, count in live["gesture_frequency"].items():
                merged_gesture_freq[gesture] = merged_gesture_freq.get(gesture, 0) + count

            total_translations = (
                db_analytics.get("total_translations", 0) + live["total_translations"]
            )
            avg_confidence = db_analytics.get("average_confidence", live["average_confidence"])

            language_dist = {**db_analytics.get("language_distribution", {})}
            for lang, count in live["language_distribution"].items():
                language_dist[lang] = language_dist.get(lang, 0) + count

            daily_activity = {**db_analytics.get("daily_activity", {})}
            for date, count in live["daily_activity"].items():
                daily_activity[date] = daily_activity.get(date, 0) + count
        else:
            merged_gesture_freq = live["gesture_frequency"]
            total_translations = live["total_translations"]
            avg_confidence = live["average_confidence"]
            language_dist = live["language_distribution"]
            daily_activity = live["daily_activity"]

        # Build chart data
        gesture_bar = self._build_gesture_bar(merged_gesture_freq)
        alphabet_heatmap = heatmap_builder.build_alphabet_heatmap(merged_gesture_freq)
        emotion_pie = heatmap_builder.build_emotion_pie_data(live["emotion_distribution"])
        confidence_bars = heatmap_builder.build_confidence_trend(live["confidence_histogram"])
        language_bar = self._build_language_bar(language_dist)
        daily_line = self._build_daily_line(daily_activity)
        hourly_bar = self._build_hourly_bar(live["hourly_activity"])

        return {
            "summary": {
                "total_translations": total_translations,
                "average_confidence": avg_confidence,
                "average_latency_ms": live["average_latency_ms"],
                "session_duration_seconds": live["session_duration_seconds"],
                "total_speech_events": live["total_speech_events"],
            },
            "gesture_bar": gesture_bar,
            "alphabet_heatmap": alphabet_heatmap,
            "emotion_pie": emotion_pie,
            "confidence_bars": confidence_bars,
            "language_bar": language_bar,
            "daily_line": daily_line,
            "hourly_bar": hourly_bar,
            "top_gestures": live["top_gestures"],
        }

    def _build_gesture_bar(self, gesture_frequency: Dict[str, int]) -> Dict[str, Any]:
        """Bar chart of top gesture frequencies."""
        sorted_g = sorted(gesture_frequency.items(), key=lambda x: x[1], reverse=True)[:15]
        return {
            "x": [g[0] for g in sorted_g],
            "y": [g[1] for g in sorted_g],
            "type": "bar",
            "color": "#D02020",
            "title": "Top 15 Gesture Frequencies",
        }

    def _build_language_bar(self, language_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Bar chart of language usage distribution."""
        sorted_l = sorted(language_distribution.items(), key=lambda x: x[1], reverse=True)
        return {
            "x": [l[0] for l in sorted_l],
            "y": [l[1] for l in sorted_l],
            "type": "bar",
            "color": "#1040C0",
            "title": "Translation Language Distribution",
        }

    def _build_daily_line(self, daily_activity: Dict[str, int]) -> Dict[str, Any]:
        """Line chart of daily translation activity."""
        sorted_d = sorted(daily_activity.items())
        return {
            "x": [d[0] for d in sorted_d],
            "y": [d[1] for d in sorted_d],
            "type": "line",
            "color": "#121212",
            "title": "Daily Translation Activity",
        }

    def _build_hourly_bar(self, hourly_activity: Dict[str, int]) -> Dict[str, Any]:
        """Bar chart of hourly activity distribution."""
        sorted_h = sorted(hourly_activity.items())
        return {
            "x": [h[0] for h in sorted_h],
            "y": [h[1] for h in sorted_h],
            "type": "bar",
            "color": "#F0C020",
            "title": "Translation Activity by Hour of Day",
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a targeted performance/latency report.

        Returns:
            Performance metrics dict
        """
        live = metrics_collector.get_full_metrics_snapshot()
        return {
            "average_latency_ms": live["average_latency_ms"],
            "average_confidence": live["average_confidence"],
            "total_events": live["total_translations"],
            "confidence_histogram": live["confidence_histogram"],
            "session_duration_minutes": round(live["session_duration_seconds"] / 60, 1),
        }


# Global singleton instance
report_generator = ReportGenerator()
