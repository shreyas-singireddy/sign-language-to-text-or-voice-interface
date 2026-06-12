"""
SignBridge AI — Layer 9: Heatmap Builder
Generates gesture frequency heatmap data for Plotly visualization.
Produces both grid-format (2D heatmap) and list-format data.
"""

from typing import Any

from config.logger import setup_logger

logger = setup_logger("analytics.heatmap_builder")

# Fixed gesture grid layout for ASL alphabet (5x6 grid + digits)
ASL_ALPHABET_GRID = [
    ["A", "B", "C", "D", "E", "F"],
    ["G", "H", "I", "J", "K", "L"],
    ["M", "N", "O", "P", "Q", "R"],
    ["S", "T", "U", "V", "W", "X"],
    ["Y", "Z", "0", "1", "2", "3"],
    ["4", "5", "6", "7", "8", "9"],
]

# Common word gestures for word-level heatmap
WORD_GESTURE_LIST = [
    "HELLO",
    "THANK",
    "PLEASE",
    "HELP",
    "SORRY",
    "YES",
    "NO",
    "WATER",
    "FOOD",
    "MEDICINE",
    "PAIN",
    "DOCTOR",
    "EMERGENCY",
    "GOOD MORNING",
    "GOOD NIGHT",
    "UNDERSTAND",
    "BATHROOM",
    "HOME",
    "HOSPITAL",
    "LOST",
    "WAIT",
    "HURRY",
]


class HeatmapBuilder:
    """
    Builds heatmap-ready data structures from gesture frequency metrics.
    Outputs Plotly-compatible z-values, x-labels, and y-labels.
    """

    def build_alphabet_heatmap(self, gesture_frequency: dict[str, int]) -> dict[str, Any]:
        """
        Build a 6x6 alphabet heatmap from gesture frequency data.

        Args:
            gesture_frequency: Dict mapping gesture name → occurrence count

        Returns:
            Dict with 'z' (2D frequency matrix), 'x' (columns), 'y' (rows),
            'text' (hover labels)
        """
        z_values = []
        text_labels = []

        for row in ASL_ALPHABET_GRID:
            z_row = []
            text_row = []
            for letter in row:
                count = gesture_frequency.get(letter, 0)
                z_row.append(count)
                text_row.append(f"{letter}: {count}")
            z_values.append(z_row)
            text_labels.append(text_row)

        x_labels = [str(i + 1) for i in range(len(ASL_ALPHABET_GRID[0]))]
        y_labels = [f"Row {i + 1}" for i in range(len(ASL_ALPHABET_GRID))]

        logger.debug("Alphabet heatmap data built.")
        return {
            "z": z_values,
            "x": x_labels,
            "y": y_labels,
            "text": text_labels,
            "colorscale": "Reds",
            "title": "ASL Alphabet Gesture Frequency Heatmap",
        }

    def build_word_heatmap(self, gesture_frequency: dict[str, int], top_n: int = 20) -> dict[str, Any]:
        """
        Build a bar-chart-ready frequency list for word gestures.

        Args:
            gesture_frequency: Dict mapping gesture name → count
            top_n: Maximum number of gestures to include

        Returns:
            Dict with 'gestures' list and 'counts' list (parallel arrays)
        """
        # Filter to known word gestures or take top-n from all gestures
        word_gestures = {k: v for k, v in gesture_frequency.items() if k in WORD_GESTURE_LIST}

        # Merge in any additional high-frequency gestures not in list
        for gesture, count in gesture_frequency.items():
            if gesture not in word_gestures:
                word_gestures[gesture] = count

        # Sort descending, take top_n
        sorted_gestures = sorted(word_gestures.items(), key=lambda x: x[1], reverse=True)[:top_n]

        gestures = [g[0] for g in sorted_gestures]
        counts = [g[1] for g in sorted_gestures]

        return {"gestures": gestures, "counts": counts}

    def build_emotion_pie_data(self, emotion_distribution: dict[str, int]) -> dict[str, Any]:
        """
        Build pie chart data from emotion distribution.

        Args:
            emotion_distribution: Dict of emotion_name → count

        Returns:
            Dict with 'labels' and 'values' for Plotly pie chart
        """
        emotion_colors = {
            "neutral": "#888888",
            "urgent": "#D02020",
            "distressed": "#1040C0",
            "grateful": "#F0C020",
            "friendly": "#20A040",
            "confused": "#E07000",
        }

        labels = list(emotion_distribution.keys())
        values = list(emotion_distribution.values())
        colors = [emotion_colors.get(label.lower(), "#AAAAAA") for label in labels]

        return {"labels": labels, "values": values, "colors": colors}

    def build_confidence_trend(self, confidence_histogram: dict[str, int]) -> dict[str, Any]:
        """
        Build confidence distribution bar chart data.

        Args:
            confidence_histogram: Dict of bucket_label → count

        Returns:
            Dict with 'buckets' and 'counts' parallel arrays
        """
        buckets = list(confidence_histogram.keys())
        counts = list(confidence_histogram.values())
        return {"buckets": buckets, "counts": counts}


heatmap_builder = HeatmapBuilder()
