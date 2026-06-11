import json
import shutil
import time
from pathlib import Path

from config.config import MODELS_DIR


class ModelRegistry:
    def __init__(self, registry_dir: Path = MODELS_DIR / "registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.registry_dir / "registry_metadata.json"
        self._initialize_metadata()

    def _initialize_metadata(self):
        if not self.metadata_file.exists():
            with open(self.metadata_file, "w") as f:
                json.dump(
                    {
                        "active_versions": {
                            "alphabet": None,
                            "word": None,
                            "sentence": None,
                        },
                        "models": [],
                    },
                    f,
                )

    def _read_metadata(self) -> dict:
        try:
            with open(self.metadata_file) as f:
                return json.load(f)
        except Exception:
            return {"active_versions": {}, "models": []}

    def _write_metadata(self, meta: dict):
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(meta, f, indent=4)
        except Exception:
            pass

    def register_model(
        self,
        model_type: str,
        model_filepath: Path,
        metrics: dict[str, float],
        classes: list[str],
        model_name: str = "LSTM",
    ) -> str:
        """
        Registers a new model version into the catalog.
        """
        model_type = model_type.lower()  # alphabet, word, sentence
        timestamp = int(time.time())
        version = f"v_{model_type}_{timestamp}"

        # Save model file into registry folder
        dest_dir = self.registry_dir / version
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_filepath = dest_dir / model_filepath.name
        shutil.copy2(model_filepath, dest_filepath)

        # Update metadata index
        registry_meta = self._read_metadata()

        model_record = {
            "version": version,
            "model_type": model_type,
            "model_name": model_name,
            "filename": model_filepath.name,
            "filepath": str(dest_filepath.relative_to(self.registry_dir)),
            "timestamp": timestamp,
            "metrics": metrics,
            "classes": classes,
        }

        registry_meta["models"].append(model_record)
        # Set as latest active by default
        registry_meta["active_versions"][model_type] = version
        self._write_metadata(registry_meta)

        return version

    def get_active_model_details(self, model_type: str) -> dict | None:
        """
        Returns catalog metadata for the active model version of a specific type.
        """
        model_type = model_type.lower()
        meta = self._read_metadata()
        active_version = meta.get("active_versions", {}).get(model_type)
        if not active_version:
            return None

        for m in meta.get("models", []):
            if m["version"] == active_version:
                return m
        return None

    def get_active_model_path(self, model_type: str) -> Path | None:
        """
        Returns absolute filepath of the active model binary.
        """
        details = self.get_active_model_details(model_type)
        if details:
            return self.registry_dir / details["filepath"]
        return None

    def list_models(self, model_type: str | None = None) -> list[dict]:
        """
        Lists registered model details.
        """
        meta = self._read_metadata()
        models = meta.get("models", [])
        if model_type:
            model_type = model_type.lower()
            return [m for m in models if m["model_type"] == model_type]
        return models

    def rollback_model(self, model_type: str, target_version: str) -> bool:
        """
        Rolls back active model target to a previously registered version.
        """
        model_type = model_type.lower()
        meta = self._read_metadata()

        # Verify target version exists
        exists = any(
            m["version"] == target_version and m["model_type"] == model_type
            for m in meta.get("models", [])
        )
        if not exists:
            return False

        meta["active_versions"][model_type] = target_version
        self._write_metadata(meta)
        return True


model_registry = ModelRegistry()
