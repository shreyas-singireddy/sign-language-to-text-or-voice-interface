import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


class Evaluator:
    def __init__(self):
        pass

    def evaluate_predictions(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        classes: list[str],
    ) -> dict[str, Any]:
        """
        Computes Accuracy, Precision, Recall, F1 Score, Confusion Matrix, Top-K Accuracy, and Class-wise statistics.
        """
        # Overall metrics
        acc = float(accuracy_score(y_true, y_pred))
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=range(len(classes)))

        # Top-K accuracy (default K=3, or K=2 if number of classes is small)
        top_k = {}
        for k in [2, 3]:
            if len(classes) >= k:
                correct = 0
                for idx, true_class in enumerate(y_true):
                    top_k_preds = np.argsort(y_prob[idx])[-k:]
                    if true_class in top_k_preds:
                        correct += 1
                top_k[f"top_{k}_accuracy"] = float(correct / len(y_true))

        # Class-wise accuracy
        class_prec, class_rec, class_f1, class_supp = precision_recall_fscore_support(
            y_true, y_pred, labels=range(len(classes)), zero_division=0
        )
        class_stats = {}
        for idx, name in enumerate(classes):
            # Calculate class accuracy: (true positives) / total samples in class
            class_mask = y_true == idx
            class_acc = float(np.mean(y_pred[class_mask] == idx)) if np.any(class_mask) else 0.0

            class_stats[name] = {
                "accuracy": class_acc,
                "precision": float(class_prec[idx]),
                "recall": float(class_rec[idx]),
                "f1_score": float(class_f1[idx]),
                "support": int(class_supp[idx]),
            }

        return {
            "accuracy": acc,
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "top_k_accuracy": top_k,
            "confusion_matrix": cm.tolist(),
            "class_wise_statistics": class_stats,
        }

    def export_report(self, metrics: dict[str, Any], filepath: Path) -> Path:
        """
        Exports metrics report as a structured JSON file.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=4)

        return filepath


evaluator = Evaluator()
