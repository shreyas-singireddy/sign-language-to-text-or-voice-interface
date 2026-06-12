import json
from pathlib import Path

import pandas as pd

from ai_engine.exporters.csv_exporter import csv_exporter
from ai_engine.utils.config import sys_config
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("exporters.parquet")


class ParquetExporter:
    def export(self, raw_session_filepath: Path) -> Path | None:
        """
        Parses raw session JSON landmarks and flattens them into a Parquet file.
        Falls back to CSV if pyarrow / fastparquet is not installed in the environment.
        """
        if not raw_session_filepath.exists():
            logger.error(f"Source file {raw_session_filepath} missing.")
            return None

        # Build rows using the CSV logic to keep it DRY
        try:
            with open(raw_session_filepath) as f:
                data = json.load(f)

            label = data.get("label", "UNKNOWN")
            frames = data.get("frames", [])

            rows = []
            for frame_id, frame in enumerate(frames):
                timestamp = frame.get("timestamp", 0.0)

                # Left Hand
                lh = frame.get("left_hand", {})
                if lh.get("present", False):
                    for idx, pt in enumerate(lh.get("landmarks", [])):
                        rows.append(
                            [
                                frame_id,
                                timestamp,
                                label,
                                "left_hand",
                                idx,
                                pt["x"],
                                pt["y"],
                                pt["z"],
                                pt["visibility"],
                            ]
                        )

                # Right Hand
                rh = frame.get("right_hand", {})
                if rh.get("present", False):
                    for idx, pt in enumerate(rh.get("landmarks", [])):
                        rows.append(
                            [
                                frame_id,
                                timestamp,
                                label,
                                "right_hand",
                                idx,
                                pt["x"],
                                pt["y"],
                                pt["z"],
                                pt["visibility"],
                            ]
                        )

                # Pose
                pose = frame.get("pose", {})
                if pose.get("present", False):
                    for idx, pt in enumerate(pose.get("landmarks", [])):
                        rows.append(
                            [
                                frame_id,
                                timestamp,
                                label,
                                "pose",
                                idx,
                                pt["x"],
                                pt["y"],
                                pt["z"],
                                pt["visibility"],
                            ]
                        )

                # Face
                face = frame.get("face", {})
                if face.get("present", False):
                    for idx, pt in enumerate(face.get("landmarks", [])):
                        rows.append(
                            [
                                frame_id,
                                timestamp,
                                label,
                                "face",
                                idx,
                                pt["x"],
                                pt["y"],
                                pt["z"],
                                pt["visibility"],
                            ]
                        )

            df = pd.DataFrame(
                rows,
                columns=[
                    "frame_id",
                    "timestamp",
                    "label",
                    "joint_type",
                    "joint_index",
                    "x",
                    "y",
                    "z",
                    "visibility",
                ],
            )

            export_dir = Path(sys_config.exports_path)
            export_dir.mkdir(parents=True, exist_ok=True)

            session_id = raw_session_filepath.parent.name
            export_filepath = export_dir / f"{session_id}_dataset.parquet"

            try:
                # Try writing as Parquet
                df.to_parquet(export_filepath, index=False)
                logger.info(f"Session data exported to Parquet: {export_filepath}")
                return export_filepath
            except ImportError:
                logger.warning("pyarrow or fastparquet not found. Falling back to CSV export instead.")
                return csv_exporter.export(raw_session_filepath)
        except Exception as e:
            logger.error(f"Failed to export Parquet: {e}")
            return None


parquet_exporter = ParquetExporter()
