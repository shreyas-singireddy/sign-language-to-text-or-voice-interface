import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from config.config import MODELS_DIR
from ai_engine.gesture_recognition.dataset.dataset_manager import dataset_manager
from ai_engine.gesture_recognition.storage.checkpoint_manager import CheckpointManager
from ai_engine.gesture_recognition.storage.model_registry import model_registry
from ai_engine.gesture_recognition.training.evaluator import evaluator
from ai_engine.gesture_recognition.models.alphabet_model import AlphabetMLP
from ai_engine.gesture_recognition.models.word_model import (
    LSTMClassifier, 
    BiLSTMClassifier, 
    TransformerClassifier, 
    TCNClassifier,
    export_word_model_onnx
)

# Safe TensorBoard import
try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    SummaryWriter = None

class GestureDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class Trainer:
    def __init__(self, model_dir: Path = MODELS_DIR):
        self.model_dir = Path(model_dir)
        self.checkpoint_mgr = CheckpointManager(self.model_dir / "checkpoints")

    def train_model(self, 
                    model_type: str = "word", 
                    arch_name: str = "LSTM", 
                    epochs: int = 15, 
                    batch_size: int = 16, 
                    lr: float = 0.001, 
                    patience: int = 5) -> Tuple[str, Dict[str, Any]]:
        """
        Orchestrates training loop for alphabet or word classifiers.
        """
        model_type = model_type.lower()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 1. Load Data
        X, y, classes = dataset_manager.load_dataset()
        num_classes = len(classes)
        input_dim = X.shape[-1]
        
        # For alphabet static models, we flatten the temporal dimension if needed
        # or train on frame-level samples. Let's make sure the shape matches the model
        if model_type == "alphabet":
            # X shape is (N, seq_len, 1662) -> reshape to (N * seq_len, 1662)
            N, seq_len, feat_dim = X.shape
            X_flat = X.reshape((N * seq_len, feat_dim))
            # Repeat labels for each frame
            y_flat = np.repeat(y, seq_len)
            
            X_train_split, X_val_split, X_test_split = dataset_manager.train_val_test_split(X_flat, y_flat)
        else:
            X_train_split, X_val_split, X_test_split = dataset_manager.train_val_test_split(X)
            
        (X_train, y_train) = X_train_split
        (X_val, y_val) = X_val_split
        (X_test, y_test) = X_test_split
        
        train_loader = DataLoader(GestureDataset(X_train, y_train), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(GestureDataset(X_val, y_val), batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(GestureDataset(X_test, y_test), batch_size=batch_size, shuffle=False)
        
        # 2. Instantiate Model
        if model_type == "alphabet":
            model = AlphabetMLP(input_dim=input_dim, num_classes=num_classes)
        else:
            if arch_name == "LSTM":
                model = LSTMClassifier(input_dim=input_dim, num_classes=num_classes)
            elif arch_name == "BiLSTM":
                model = BiLSTMClassifier(input_dim=input_dim, num_classes=num_classes)
            elif arch_name == "Transformer":
                model = TransformerClassifier(input_dim=input_dim, num_classes=num_classes)
            elif arch_name == "TCN":
                model = TCNClassifier(input_dim=input_dim, num_classes=num_classes)
            else:
                model = LSTMClassifier(input_dim=input_dim, num_classes=num_classes)
                
        model.to(device)
        
        # 3. Setup Optimizer and Loss
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
        
        # Setup Logger
        writer = SummaryWriter(log_dir=str(self.model_dir / "logs")) if SummaryWriter else None
        
        # 4. Training Loop
        best_val_loss = float("inf")
        epochs_no_improve = 0
        best_model_state = None
        
        for epoch in range(1, epochs + 1):
            model.train()
            train_loss = 0.0
            
            for inputs, targets in train_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * inputs.size(0)
                
            train_loss /= len(train_loader.dataset)
            
            # Validation
            model.eval()
            val_loss = 0.0
            val_correct = 0
            
            with torch.no_grad():
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(device), targets.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)
                    val_loss += loss.item() * inputs.size(0)
                    preds = torch.argmax(outputs, dim=1)
                    val_correct += (preds == targets).sum().item()
                    
            val_loss /= len(val_loader.dataset)
            val_acc = val_correct / len(val_loader.dataset)
            
            scheduler.step(val_loss)
            
            # Logs
            if writer:
                writer.add_scalar("Loss/Train", train_loss, epoch)
                writer.add_scalar("Loss/Val", val_loss, epoch)
                writer.add_scalar("Accuracy/Val", val_acc, epoch)
                
            # Early Stopping Check
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                epochs_no_improve = 0
                best_model_state = {k: v.cpu() for k, v in model.state_dict().items()}
                # Save checkpoint
                self.checkpoint_mgr.save_checkpoint(
                    model, optimizer, epoch, 
                    {"train_loss": train_loss, "val_loss": val_loss, "val_accuracy": val_acc}
                )
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    break
                    
        # 5. Evaluate on Test set using best weights
        if best_model_state:
            model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})
            
        model.eval()
        test_preds = []
        test_targets = []
        test_probs = []
        
        with torch.no_grad():
            for inputs, targets in test_loader:
                inputs = inputs.to(device)
                outputs = model(inputs)
                probs = torch.softmax(outputs, dim=1)
                preds = torch.argmax(outputs, dim=1)
                
                test_preds.extend(preds.cpu().numpy())
                test_targets.extend(targets.numpy())
                test_probs.extend(probs.cpu().numpy())
                
        metrics = evaluator.evaluate_predictions(
            np.array(test_targets), 
            np.array(test_preds), 
            np.array(test_probs), 
            classes
        )
        
        # Save model binary
        model_name = f"{model_type}_classifier.pt"
        model_path = self.model_dir / model_name
        torch.save(best_model_state, model_path)
        
        # Register Model
        reg_version = model_registry.register_model(
            model_type=model_type,
            model_filepath=model_path,
            metrics={"test_accuracy": metrics["accuracy"], "test_f1": metrics["f1_score"]},
            classes=classes,
            model_name=arch_name
        )
        
        # Export to ONNX for runtime efficiency
        onnx_name = f"{model_type}_classifier.onnx"
        onnx_path = self.model_dir / onnx_name
        
        if model_type == "alphabet":
            model.cpu()
            model.export_onnx(onnx_path)
        else:
            model.cpu()
            export_word_model_onnx(model, onnx_path, seq_len=30)
            
        if writer:
            writer.close()
            
        return reg_version, metrics

trainer = Trainer()
