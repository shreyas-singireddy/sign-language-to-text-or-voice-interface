import torch
from pathlib import Path
from typing import Dict, Any, Optional

class CheckpointManager:
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, model: torch.nn.Module, optimizer: torch.optim.Optimizer, epoch: int, metrics: Dict[str, float], filename: str = "checkpoint.pt") -> Path:
        """
        Saves full PyTorch model state and optimizer configs to disk.
        """
        filepath = self.checkpoint_dir / filename
        state = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "metrics": metrics
        }
        torch.save(state, filepath)
        return filepath

    def load_checkpoint(self, filepath: Path, model: torch.nn.Module, optimizer: Optional[torch.optim.Optimizer] = None) -> Dict[str, Any]:
        """
        Restores model state from checkpoint.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint not found at: {filepath}")
            
        state = torch.load(filepath, map_location="cpu")
        model.load_state_dict(state["model_state_dict"])
        
        if optimizer is not None and "optimizer_state_dict" in state:
            optimizer.load_state_dict(state["optimizer_state_dict"])
            
        return {
            "epoch": state.get("epoch", 0),
            "metrics": state.get("metrics", {})
        }
