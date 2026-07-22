"""Training loop and trainer with callback support."""

import os
from typing import Any, Dict, List, Optional

import torch
from torch import nn
from torch.utils.data import DataLoader


class Trainer:
    """
    Training loop with callback support.

    The training pipeline:
    - on_training_start
    - for each epoch:
        - on_epoch_start
        - for each batch: forward, backward, step
        - validate (if val_loader provided)
        - on_epoch_end
    - on_training_end
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        criterion: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        callbacks: Optional[List[Any]] = None,
        device: Optional[str] = None,
        max_grad_norm: Optional[float] = None,
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model.to(self.device)

        # Setup criterion
        if criterion is not None:
            self.criterion = criterion
        elif hasattr(model, "config") and model.config.get("num_classes", 10) >= 2:
            self.criterion = nn.CrossEntropyLoss()
        else:
            self.criterion = nn.MSELoss()

        # Setup optimizer if not provided
        if optimizer is None:
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        else:
            self.optimizer = optimizer

        self.callbacks = callbacks or []
        for cb in self.callbacks:
            if hasattr(cb, "setup"):
                cb.setup(self)

        self.max_grad_norm = max_grad_norm
        self.epoch = 0
        self.global_step = 0
        self.trained = False

    def train(
        self,
        epochs: int = 10,
        verbose: bool = True,
    ) -> Dict[str, List[float]]:
        """Run training."""
        self.num_epochs = epochs

        for cb in self.callbacks:
            if hasattr(cb, "on_training_start"):
                cb.on_training_start()

        history = {
            "loss": [],
            "accuracy": [],
            "val_loss": [],
            "val_accuracy": [],
            "epoch": [],
        }

        for epoch in range(epochs):
            self.epoch = epoch
            for cb in self.callbacks:
                if hasattr(cb, "on_epoch_start"):
                    cb.on_epoch_start(epoch)
            epoch_metrics = self._train_epoch(verbose=verbose)

            if self.val_loader is not None:
                val_metrics = self.validate()
                history["val_loss"].append(val_metrics.get("loss", 0.0))
                history["val_accuracy"].append(val_metrics.get("accuracy", 0.0))
                for cb in self.callbacks:
                    if hasattr(cb, "on_validation_end"):
                        cb.on_validation_end(val_metrics)
            else:
                val_metrics = {}

            combined = {**epoch_metrics, **{f"val_{k}": v for k, v in val_metrics.items()}, "epoch": epoch}

            # Check for early stopping
            for cb in self.callbacks:
                if getattr(cb, "early_stop", False):
                    break
            for cb in self.callbacks:
                if hasattr(cb, "on_epoch_end"):
                    cb.on_epoch_end(epoch, combined)

            history["loss"].append(epoch_metrics.get("loss", 0.0))
            history["accuracy"].append(epoch_metrics.get("accuracy", 0.0))
            history["epoch"].append(epoch)

        for cb in self.callbacks:
            if hasattr(cb, "on_training_end"):
                cb.on_training_end(history)

        self.trained = True
        return history

    def _train_epoch(self, verbose: bool = False) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        num_batches = len(self.train_loader) if hasattr(self.train_loader, "__len__") else 1

        for batch_idx, batch in enumerate(self.train_loader):
            x, y = self._unpack_batch(batch)

            if isinstance(x, torch.Tensor):
                x = x.to(self.device)
            if isinstance(y, torch.Tensor):
                y = y.to(self.device)

            outputs = self.model(x)

            if y is not None:
                loss = self.criterion(outputs, y)
            else:
                loss = torch.tensor(0.0, device=self.device)

            self.optimizer.zero_grad()
            if loss.requires_grad:
                loss.backward()

            if self.max_grad_norm is not None:
                nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)

            self.optimizer.step()

            total_loss += loss.item()

            if y is not None and isinstance(outputs, torch.Tensor):
                total_correct += Trainer._compute_correct(outputs, y)
                total_samples += y.size(0)

            for cb in self.callbacks:
                if hasattr(cb, "on_batch_end"):
                    cb.on_batch_end(batch_idx, {"loss": loss.item()}, batch)

        avg_loss = total_loss / max(num_batches, 1)
        accuracy = total_correct / max(total_samples, 1) if total_samples > 0 else 0.0
        return {"loss": avg_loss, "accuracy": accuracy}

    def validate(self) -> Dict[str, float]:
        """Run validation."""
        self.model.eval()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        with torch.no_grad():
            for batch in self.val_loader:
                x, y = self._unpack_batch(batch)
                if isinstance(x, torch.Tensor):
                    x = x.to(self.device)
                if isinstance(y, torch.Tensor):
                    y = y.to(self.device)

                outputs = self.model(x)
                loss = self.criterion(outputs, y) if y is not None else torch.tensor(0.0)
                total_loss += loss.item()

                if y is not None and isinstance(outputs, torch.Tensor):
                    total_correct += Trainer._compute_correct(outputs, y)
                    total_samples += y.size(0)

        num_batches = len(self.val_loader) if hasattr(self.val_loader, "__len__") else 1
        avg_loss = total_loss / max(num_batches, 1)
        accuracy = total_correct / max(total_samples, 1) if total_samples > 0 else 0.0
        return {"loss": avg_loss, "accuracy": accuracy}

    @staticmethod
    def _compute_correct(outputs: torch.Tensor, y: torch.Tensor) -> int:
        """Compute number of correct predictions for a batch."""
        preds = (
            outputs.argmax(dim=1)
            if outputs.dim() > 1
            else (outputs > 0.5).float()
        )
        return (preds == y).sum().item()

    @staticmethod
    def _unpack_batch(batch):
        """Extract (x, y) from a batch, supporting dict and tuple formats."""
        if isinstance(batch, dict):
            x = batch.get("x", batch.get("image", batch.get("input", batch.get("data"))))
            y = batch.get("y", batch.get("label", batch.get("target")))
            if x is None:
                for key in ["input_ids", "features"]:
                    if key in batch:
                        x = batch[key]
                        break
        else:
            x = batch[0]
            y = batch[1] if len(batch) > 1 else None
        return x, y

    def save_checkpoint(self, path: str) -> None:
        """Save model checkpoint."""
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        if hasattr(self.model, "get_params"):
            state = self.model.get_params()
        else:
            state = self.model.state_dict()
        torch.save(state, path)

    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint."""
        state = torch.load(path, weights_only=True)
        if hasattr(self.model, "set_model_params"):
            self.model.set_model_params(state)
        else:
            self.model.load_state_dict(state)
