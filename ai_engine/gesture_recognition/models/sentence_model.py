from typing import Any

import torch
from torch import nn


class SentenceCTCModel(nn.Module):
    def __init__(
        self, input_dim: int = 1662, hidden_dim: int = 128, num_classes: int = 15
    ):
        """
        CTC-style sequence model that processes continuous sequences of frame landmarks
        and outputs character or word probabilities for Connectionist Temporal Classification (CTC) decoding.
        """
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
        )
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: (batch_size, sequence_length, input_dim)
        lstm_out, _ = self.lstm(x)  # shape: (batch_size, seq_len, hidden_dim * 2)
        logits = self.fc(lstm_out)  # shape: (batch_size, seq_len, num_classes)
        return logits


class SentenceDecoder:
    def __init__(self):
        pass

    def decode_transitions(
        self,
        predictions_history: list[dict[str, Any]],
        velocity_history: list[float],
        confidence_threshold: float = 0.8,
    ) -> str:
        """
        Performs continuous sequence segmentation.
        Uses motion boundaries (velocity dips) and label changes to segment words
        and assemble a structured output sentence.
        """
        if not predictions_history:
            return ""

        words = []
        current_word = None
        consecutive_frames = 0
        min_stable_frames = 8

        # Scan historical frame predictions
        for idx, item in enumerate(predictions_history):
            label = item.get("prediction", "IDLE")
            conf = item.get("confidence", 0.0)

            # Use velocity thresholds to identify transition pauses between gestures
            is_transition = False
            if idx < len(velocity_history):
                vel = velocity_history[idx]
                # A velocity dip represents a brief pause, indicating gesture completion
                if vel < 0.05:
                    is_transition = True

            if label == "IDLE" or conf < confidence_threshold or is_transition:
                if current_word and consecutive_frames >= min_stable_frames:
                    if not words or words[-1] != current_word:
                        words.append(current_word)
                current_word = None
                consecutive_frames = 0
                continue

            if label == current_word:
                consecutive_frames += 1
            else:
                if current_word and consecutive_frames >= min_stable_frames:
                    if not words or words[-1] != current_word:
                        words.append(current_word)
                current_word = label
                consecutive_frames = 1

        # Catch tail
        if current_word and consecutive_frames >= min_stable_frames:
            if not words or words[-1] != current_word:
                words.append(current_word)

        # Remove blanks or temporary markers
        words = [w for w in words if w not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE"]]
        return " ".join(words)


sentence_decoder = SentenceDecoder()
