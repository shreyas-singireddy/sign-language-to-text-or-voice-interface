import torch
import torch.nn as nn
import time
from pathlib import Path
from typing import Dict, Any

# ==========================================
# MODEL A: LSTM
# ==========================================
class LSTMClassifier(nn.Module):
    def __init__(self, input_dim: int = 1662, hidden_dim: int = 128, num_layers: int = 2, num_classes: int = 10):
        super(LSTMClassifier, self).__init__()
        self.input_dim = input_dim
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0
        )
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        # Take the last time step output: (batch_size, hidden_dim)
        out = lstm_out[:, -1, :]
        return self.fc(out)


# ==========================================
# MODEL B: Bidirectional LSTM
# ==========================================
class BiLSTMClassifier(nn.Module):
    def __init__(self, input_dim: int = 1662, hidden_dim: int = 128, num_layers: int = 2, num_classes: int = 10):
        super(BiLSTMClassifier, self).__init__()
        self.input_dim = input_dim
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.2 if num_layers > 1 else 0.0
        )
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        out = lstm_out[:, -1, :]  # shape: (batch_size, hidden_dim * 2)
        return self.fc(out)


# ==========================================
# MODEL C: Transformer Encoder
# ==========================================
class TransformerClassifier(nn.Module):
    def __init__(self, input_dim: int = 1662, hidden_dim: int = 128, num_heads: int = 4, num_layers: int = 2, num_classes: int = 10):
        super(TransformerClassifier, self).__init__()
        self.input_dim = input_dim
        
        # Project input to hidden dimension
        self.input_projection = nn.Linear(input_dim, hidden_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 2,
            dropout=0.2,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_dim)
        projected = self.input_projection(x)  # shape: (batch_size, seq_len, hidden_dim)
        transformer_out = self.transformer(projected)  # shape: (batch_size, seq_len, hidden_dim)
        
        # Average pooling over seq_len
        pooled = torch.mean(transformer_out, dim=1)  # shape: (batch_size, hidden_dim)
        return self.fc(pooled)


# ==========================================
# MODEL D: Temporal Convolution Network (TCN)
# ==========================================
class ChinnedResidualBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int, stride: int, dilation: int, padding: int, dropout: float = 0.2):
        super(ChinnedResidualBlock, self).__init__()
        # Causal convolution is achieved by shifting/padding appropriately
        self.conv1 = nn.utils.weight_norm(nn.Conv1d(
            in_channels, out_channels, kernel_size,
            stride=stride, padding=padding, dilation=dilation
        ))
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)
        
        self.conv2 = nn.utils.weight_norm(nn.Conv1d(
            out_channels, out_channels, kernel_size,
            stride=stride, padding=padding, dilation=dilation
        ))
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)
        
        self.net = nn.Sequential(
            self.conv1, self.relu1, self.dropout1,
            self.conv2, self.relu2, self.dropout2
        )
        self.downsample = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else None
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        
        # Truncate out if padding caused mismatch in length due to dilation
        if out.size(-1) != res.size(-1):
            out = out[:, :, :res.size(-1)]
            
        return self.relu(out + res)

class TCNClassifier(nn.Module):
    def __init__(self, input_dim: int = 1662, num_channels: list = [128, 64], kernel_size: int = 3, num_classes: int = 10, dropout: float = 0.2):
        super(TCNClassifier, self).__init__()
        self.input_dim = input_dim
        
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = input_dim if i == 0 else num_channels[i-1]
            out_channels = num_channels[i]
            padding = (kernel_size - 1) * dilation_size
            
            layers.append(ChinnedResidualBlock(
                in_channels, out_channels, kernel_size,
                stride=1, dilation=dilation_size, padding=padding,
                dropout=dropout
            ))
            
        self.tcn = nn.Sequential(*layers)
        self.fc = nn.Linear(num_channels[-1], num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Conv1d expects shape: (batch_size, channels, seq_len)
        # Input x shape: (batch_size, seq_len, input_dim)
        x_transposed = x.transpose(1, 2)
        tcn_out = self.tcn(x_transposed)  # shape: (batch_size, out_channels, seq_len_dilated)
        
        # Pool across temporal dimension
        pooled = torch.mean(tcn_out, dim=2)  # shape: (batch_size, out_channels)
        return self.fc(pooled)


# ==========================================
# ONNX EXPORTER UTILITY
# ==========================================
def export_word_model_onnx(model: nn.Module, filepath: Path, seq_len: int = 30) -> bool:
    """
    Exports a word classification model to ONNX format.
    """
    model.eval()
    dummy_input = torch.randn(1, seq_len, model.input_dim)
    try:
        torch.onnx.export(
            model,
            dummy_input,
            str(filepath),
            input_names=["landmark_sequence"],
            output_names=["probabilities"],
            dynamic_axes={"landmark_sequence": {0: "batch_size"}, "probabilities": {0: "batch_size"}},
            opset_version=11
        )
        return True
    except Exception as e:
        from ai_engine.utils.logger import get_structured_logger
        logger = get_structured_logger("models.word")
        logger.error(f"Failed to export Word model to ONNX: {e}")
        return False


# ==========================================
# BENCHMARK ENGINE
# ==========================================
def benchmark_model(model: nn.Module, seq_len: int = 30, runs: int = 100) -> Dict[str, Any]:
    """
    Benchmarks model inference latency and memory requirements.
    """
    model.eval()
    dummy_input = torch.randn(1, seq_len, model.input_dim)
    
    # Warmup
    for _ in range(10):
        _ = model(dummy_input)
        
    t_start = time.perf_counter()
    with torch.no_grad():
        for _ in range(runs):
            _ = model(dummy_input)
    t_end = time.perf_counter()
    
    avg_latency_ms = ((t_end - t_start) / runs) * 1000.0
    
    # Approximate parameter footprint
    params_count = sum(p.numel() for p in model.parameters())
    memory_kb = (params_count * 4) / 1024.0  # Float32 is 4 bytes
    
    return {
        "average_latency_ms": round(avg_latency_ms, 3),
        "parameters": params_count,
        "memory_footprint_kb": round(memory_kb, 2)
    }
