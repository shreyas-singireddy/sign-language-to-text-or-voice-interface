import shutil
from pathlib import Path

from ai_engine.utils.config import sys_config
from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("exporters.json")


class JsonExporter:
    def export(self, raw_session_filepath: Path) -> Path | None:
        """
        Copies recorded raw landmark json file to public exports folder.
        """
        if not raw_session_filepath.exists():
            logger.error("Source file does not exist.")
            return None

        export_dir = Path(sys_config.exports_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        session_id = raw_session_filepath.parent.name
        export_filepath = export_dir / f"{session_id}_dataset.json"

        try:
            shutil.copy2(raw_session_filepath, export_filepath)
            logger.info(f"Session data exported to JSON: {export_filepath}")
            return export_filepath
        except Exception as e:
            logger.error(f"Failed to export JSON file: {e}")
            return None


json_exporter = JsonExporter()
