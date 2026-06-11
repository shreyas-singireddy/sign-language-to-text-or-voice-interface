import itertools
from typing import Any

from ai_engine.gesture_recognition.training.trainer import trainer


class HyperparameterTuner:
    def __init__(self):
        pass

    def tune_hyperparameters(
        self,
        model_type: str = "word",
        arch_name: str = "LSTM",
        search_space: dict[str, list[Any]] = None,
    ) -> tuple[dict[str, Any], float]:
        """
        Runs Grid Search over learning rate, hidden dim, and batch size options.
        Returns the best configuration dict and its validation accuracy.
        """
        if search_space is None:
            search_space = {
                "lr": [0.01, 0.001],
                "batch_size": [16, 32],
                "epochs": [3],  # Short training duration during tuning search
            }

        keys, values = zip(*search_space.items())
        experiments = [dict(zip(keys, v)) for v in itertools.product(*values)]

        best_accuracy = -1.0
        best_params = {}

        for exp in experiments:
            try:
                # Trigger training run
                _, metrics = trainer.train_model(
                    model_type=model_type,
                    arch_name=arch_name,
                    epochs=exp.get("epochs", 5),
                    batch_size=exp.get("batch_size", 16),
                    lr=exp.get("lr", 0.001),
                )

                acc = metrics.get("accuracy", 0.0)
                if acc > best_accuracy:
                    best_accuracy = acc
                    best_params = exp
            except Exception:
                continue

        return best_params, best_accuracy


hyperparameter_tuner = HyperparameterTuner()
