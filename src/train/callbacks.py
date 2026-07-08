"""Training callbacks."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import torch
from torch.utils.tensorboard import SummaryWriter

logger = logging.getLogger(__name__)


class Callback:
    """Base callback class."""

    def __init__(self):
        """Initialize callback."""
        super().__init__()
        self.enabled = True

    def setup(self, trainer):
        """
        Setup callback with trainer.

        Args:
            trainer: Trainer instance
        """
        self.trainer = trainer

    def on_epoch_start(self, epoch):
        """
        Called at the start of each epoch.

        Args:
            epoch: Current epoch number
        """
        pass

    def on_epoch_end(self, epoch, metrics):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
        pass

    def on_batch_start(self, batch_idx):
        """
        Called at the start of each batch.

        Args:
            batch_idx: Batch index
        """
        pass

    def on_batch_end(self, batch_idx, outputs, batch):
        """
        Called at the end of each batch.

        Args:
            batch_idx: Batch index
            outputs: Batch outputs
            batch: Batch inputs
        """
        pass

    def on_training_start(self):
        """Called at the start of training."""
        pass

    def on_validation_start(self):
        """Called at the start of validation."""
        pass

    def on_validation_end(self, metrics):
        """
        Called at the end of validation.

        Args:
            metrics: Validation metrics
        """
        pass

    def on_training_end(self, metrics):
        """Called at the end of training."""
        pass

    def on_exception(self, exception):
        """
        Called when exception occurs.

        Args:
            exception: Exception object
        """
        pass

    def state_dict(self):
        """Get callback state dict."""
        return {k: v for k, v in self.__dict__.items() if isinstance(v, (dict, list))}

    def load_state_dict(self, state_dict):
        """
        Load state dict.

        Args:
            state_dict: State dict to load
        """
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)


class EarlyStopping(Callback):
    """Early stopping callback."""

    def __init__(self, patience: int = 7, min_delta: float = 0.0, mode: str = 'min'):
        """
        Initialize early stopping callback.

        Args:
            patience: Number of epochs to wait
            min_delta: Minimum improvement
            mode: 'min' or 'max'
        """
        super().__init__()
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode

        self.best: Optional[float] = None
        self.counter = 0
        self.early_stop = False

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        if self.mode == 'min':
            self.best = float('inf')
        else:
            self.best = float('-inf')

    def on_epoch_end(self, epoch, metrics: Dict[str, float]):
        """Called at the end of each epoch."""
        if not self.enabled:
            return

        val_metric = metrics.get('val_loss', metrics.get('val_accuracy', None))
        if val_metric is None:
            return

        if self.mode == 'min':
            if val_metric < self.best - self.min_delta:
                self.best = val_metric
                self.counter = 0
            else:
                self.counter += 1
        else:
            if val_metric > self.best + self.min_delta:
                self.best = val_metric
                self.counter = 0
            else:
                self.counter += 1

        if self.counter >= self.patience:
            self.early_stop = True

    def on_training_end(self, history: Dict[str, list]):
        """Called at the end of training."""
        if self.early_stop:
            last_epoch = history.get('epoch', [None])[-1] if isinstance(history.get('epoch'), list) else '?'
            logger.warning("Early stopping triggered at epoch %s. Best value: %s",
                           last_epoch, self.best)

    def state_dict(self):
        """Get state dict."""
        return {
            'patience': self.patience,
            'min_delta': self.min_delta,
            'mode': self.mode,
            'best': self.best,
            'counter': self.counter,
            'early_stop': self.early_stop,
        }

    def load_state_dict(self, state_dict):
        """Load state dict."""
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)


class ModelCheckpoint(Callback):
    """Model checkpoint with automatic best model tracking."""

    def __init__(
        self,
        save_path: str = None,
        save_top_k: int = 3,
        monitor: str = 'val_loss',
        mode: str = 'min',
        filename: str = None,
        every_n_epochs: int = -1,
    ):
        """
        Initialize model checkpoint.

        Args:
            save_path: Path to save checkpoints
            save_top_k: Number of best models to save
            monitor: Metric to monitor
            mode: 'min' or 'max'
            filename: Checkpoint filename format
            every_n_epochs: Save every n epochs (-1: only when best)
        """
        super().__init__()
        self.save_path = save_path
        self.save_top_k = save_top_k
        self.monitor = monitor
        self.mode = mode
        self.filename = filename or 'epoch_{epoch}'
        self.every_n_epochs = every_n_epochs

        self.best: Optional[float] = None
        self.epochs_since_best = 0

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        if self.mode == 'min':
            self.best = float('inf')
        else:
            self.best = float('-inf')

    def on_validation_end(self, metrics: Dict[str, float]):
        """Called at the end of validation."""
        if not self.enabled:
            return

        if self.every_n_epochs > 0 and metrics.get('epoch', 0) % self.every_n_epochs != 0:
            return

        val_metric = metrics.get(self.monitor, metrics.get('val_loss', None))
        if val_metric is None:
            return

        if self.mode == 'min':
            if val_metric < self.best:
                self.best = val_metric
                self.epochs_since_best = 0
                self._save_checkpoint(metrics)
            else:
                self.epochs_since_best += 1
        else:
            if val_metric > self.best:
                self.best = val_metric
                self.epochs_since_best = 0
                self._save_checkpoint(metrics)
            else:
                self.epochs_since_best += 1

    def _save_checkpoint(self, metrics: Dict[str, float]):
        """Save checkpoint."""
        if self.save_path is None:
            return

        os.makedirs(self.save_path, exist_ok=True)
        save_path = os.path.join(self.save_path, f'{self.filename.format(epoch=metrics.get("epoch", 0))}.pt')
        torch.save(self.trainer.model.state_dict(), save_path)

        checkpoint_path = save_path.replace('.pt', '.json')
        with open(checkpoint_path, 'w') as f:
            json.dump({'metrics': metrics, 'best': self.best}, f)

    def state_dict(self):
        """Get state dict."""
        return {
            'save_path': self.save_path,
            'save_top_k': self.save_top_k,
            'monitor': self.monitor,
            'mode': self.mode,
            'filename': self.filename,
            'best': self.best,
            'epochs_since_best': self.epochs_since_best,
            'every_n_epochs': self.every_n_epochs,
        }

    def load_state_dict(self, state_dict: Dict[str, Any]):
        """Load state dict."""
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)


class LearningRateScheduler(Callback):
    """Learning rate scheduler callback."""

    def __init__(
        self,
        factor: float = 0.1,
        patience: int = 5,
        min_lr: float = 1e-8,
    ):
        """
        Initialize learning rate scheduler.

        Args:
            factor: Factor to multiply LR
            patience: Number of epochs to wait
            min_lr: Minimum LR
        """
        super().__init__()
        self.factor = factor
        self.patience = patience
        self.min_lr = min_lr

        self.counter = 0
        self.best_loss: Optional[float] = None

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """Called at the end of each epoch."""
        loss = metrics.get('loss', None)
        if loss is None:
            return

        if self.best_loss is None or loss < self.best_loss - self.min_delta:
            self.best_loss = loss
            self.counter = 0
        else:
            self.counter += 1

        if self.counter >= self.patience:
            for param_group in self.trainer.optimizer.param_groups:
                old_lr = param_group['lr']
                new_lr = max(self.min_lr, old_lr * self.factor)
                param_group['lr'] = new_lr
                logger.info("LR reduced: %.2e → %.2e (epoch %d)", old_lr, new_lr, epoch)
            self.counter = 0

    def state_dict(self):
        """Get state dict."""
        return {
            'factor': self.factor,
            'patience': self.patience,
            'min_lr': self.min_lr,
            'counter': self.counter,
            'best_loss': self.best_loss,
        }

    def load_state_dict(self, state_dict):
        """Load state dict."""
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)


class TensorBoardLogger(Callback):
    """TensorBoard logging callback."""

    def __init__(self, log_dir: str = None, name: str = None):
        """
        Initialize TensorBoard logger.

        Args:
            log_dir: Log directory
            name: Name suffix
        """
        super().__init__()
        self.log_dir = log_dir or 'logs'
        self.name = name or 'exp'

        self.writer: Optional[SummaryWriter] = None

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        model_name = type(trainer.model).__name__ if hasattr(trainer, 'model') and trainer.model else 'model'
        self.writer = SummaryWriter(
            os.path.join(self.log_dir, f'{model_name}-{self.name}'),
        )

    def on_epoch_start(self, epoch):
        """
        Called at the start of each epoch.

        Args:
            epoch: Current epoch number
        """
        if self.writer is None:
            return

        self.writer.add_scalar('epoch', epoch, epoch)

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """Called at the end of each epoch."""
        if self.writer is None:
            return
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'{key}/{key}', value, epoch)

    def on_training_end(self, history):
        """Called at the end of training."""
        if self.writer is not None:
            self.writer.close()

    def state_dict(self):
        """Get state dict."""
        return {
            'log_dir': self.log_dir,
            'name': self.name,
        }

    def load_state_dict(self, state_dict):
        """Load state dict."""
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)


class ProgressLogger(Callback):
    """Progress bar callback."""

    def __init__(self, enabled: bool = True, refresh_rate: int = 10):
        """
        Initialize progress logger.

        Args:
            enabled: Whether to enable progress logging
            refresh_rate: Number of steps between updates
        """
        super().__init__()
        self.enabled = enabled
        self.refresh_rate = refresh_rate

        self.total_steps = 0
        self.current_step = 0
        self.last_update = 0

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        self.total_steps = trainer.total_steps if hasattr(trainer, 'total_steps') else 0
        self.total_epochs = trainer.num_epochs if hasattr(trainer, 'num_epochs') else 1

    def on_batch_end(self, batch_idx, outputs, batch):
        """
        Called at the end of each batch.

        Args:
            batch_idx: Batch index
            outputs: Batch outputs
            batch: Batch inputs
        """
        if not self.enabled:
            return

        self.current_step = self.current_step + 1

        if (self.current_step - self.last_update) >= self.refresh_rate:
            progress = self.current_step / self.total_steps * 100 if self.total_steps > 0 else 0
            print(f'Epoch {getattr(self, "epoch", "?")}: {self.current_step}/{self.total_steps} ({progress:.1f}%)')
            self.last_update = self.current_step

    def on_epoch_start(self, epoch):
        """
        Called at the start of each epoch.

        Args:
            epoch: Current epoch number
        """
        if not self.enabled:
            return

        self.epoch = epoch
        print(f'\nEpoch {epoch}/{self.total_epochs}')
        print('=' * 50)

    def on_epoch_end(self, epoch, metrics):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
        if not self.enabled:
            return

        # Print epoch summary
        print('=' * 50)
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                print(f'{k}: {v:.4f}')


class PrintMetrics(Callback):
    """Print metrics callback."""

    def __init__(self, metrics: List[str] = None):
        """
        Initialize print metrics callback.

        Args:
            metrics: List of metrics to print
        """
        super().__init__()
        self.metrics = metrics or []

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """Called at the end of each epoch."""
        if not self.enabled:
            return

        for key in self.metrics:
            value = metrics.get(key)
            if value is not None and isinstance(value, (int, float)):
                print(f'{key}: {value:.4f}')

    def on_validation_end(self, metrics: Dict[str, float]):
        """
        Called at the end of validation.

        Args:
            metrics: Validation metrics
        """
        if not self.enabled:
            return

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                print(f'{key}: {value:.4f}')

    def state_dict(self):
        """Get state dict."""
        return {
            'metrics': self.metrics,
        }

    def load_state_dict(self, state_dict):
        """Load state dict."""
        for k, v in state_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)
