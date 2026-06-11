import json
import pandas as pd
from pathlib import Path
from typing import Optional
from ai_engine.utils.logger import get_structured_logger
from ai_engine.utils.config import sys_config

logger = get_structured_logger("exporters.csv")

class CsvExporter:
    def export(self, raw_session_filepath: Path) -> Optional[Path]:
        """
        Parses raw session JSON landmarks and flattens them into a tabular CSV file.
        Columns: frame_id, timestamp, label, joint_type, joint_index, x, y, z, visibility
        """
        if not raw_session_filepath.exists():
            logger.error(f"Source file {raw_session_filepath} missing.")
            return None

        try:
            with open(raw_session_filepath, "r") as f:
                data = json.load(f)
            
            label = data.get("label", "UNKNOWN")
            frames = data.get("frames", [])
            
            rows = []
            
            for frame_id, frame in enumerate(frames):
                timestamp = frame.get("timestamp", 0.0)
                
                # Flatten Left Hand
                lh = frame.get("left_hand", {})
                if lh.get("present", False):
                    for idx, pt in enumerate(lh.get("landmarks", [])):
                        rows.append([frame_id, timestamp, label, "left_hand", idx, pt["x"], pt["y"], pt["z"], pt["visibility"]])
                
                # Flatten Right Hand
                rh = frame.get("right_hand", {})
                if rh.get("present", False):
                    for idx, pt in enumerate(rh.get("landmarks", [])):
                        rows.append([frame_id, timestamp, label, "right_hand", idx, pt["x"], pt["y"], pt["z"], pt["visibility"]])
                
                # Flatten Pose
                pose = frame.get("pose", {})
                if pose.get("present", False):
                    for idx, pt in enumerate(pose.get("landmarks", [])):
                        rows.append([frame_id, timestamp, label, "pose", idx, pt["x"], pt["y"], pt["z"], pt["visibility"]])
                
                # Flatten Face
                face = frame.get("face", {})
                if face.get("present", False):
                    for idx, pt in enumerate(face.get("landmarks", [])):
                        rows.append([frame_id, timestamp, label, "face", idx, pt["x"], pt["y"], pt["z"], pt["visibility"]])

            df = pd.DataFrame(rows, columns=[
                "frame_id", "timestamp", "label", "joint_type", "joint_index", "x", "y", "z", "visibility"
            ])

            export_dir = Path(sys_config.exports_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            session_id = raw_session_filepath.parent.name
            export_filepath = export_dir / f"{session_id}_dataset.csv"
            
            df.to_csv(export_filepath, index=False)
            logger.info(f"Session data exported to CSV: {export_filepath}")
            return export_filepath
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return None

csv_exporter = CsvExporter()
