from pathlib import Path

import torch
import torch.onnx
from torch import nn


class AlphabetMLP(nn.Module):
    def __init__(self, input_dim: int = 1662, hidden_dim: int = 256, num_classes: int = 36):
        """
        PyTorch Multi-Layer Perceptron for static alphabet (A-Z, 0-9) gesture classification.
        """
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Handle single frame without batch dimension
        if x.dim() == 1:
            x = x.unsqueeze(0)
        return self.network(x)

    def export_onnx(self, filepath: Path) -> bool:
        """
        Exports the model to ONNX format.
        """
        self.eval()
        dummy_input = torch.randn(1, self.input_dim)
        try:
            torch.onnx.export(
                self,
                dummy_input,
                str(filepath),
                input_names=["landmarks"],
                output_names=["probabilities"],
                dynamic_axes={
                    "landmarks": {0: "batch_size"},
                    "probabilities": {0: "batch_size"},
                },
                opset_version=11,
            )
            return True
        except Exception as e:
            # Import logger locally to prevent circular deps
            from ai_engine.utils.logger import get_structured_logger

            logger = get_structured_logger("models.alphabet")
            logger.error(f"Failed to export Alphabet model to ONNX: {e}")
            return False
