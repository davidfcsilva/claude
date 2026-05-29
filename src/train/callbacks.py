"""Training callbacks."""

import os
import time
import json
from typing import Callable, Optional, List, Dict, Any

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from tensorboardX import SummaryWriter as TBXWriter


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
        pass

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

    def on_training_epoch_start(self, epoch):
        """
        Called at the start of each epoch.

        Args:
            epoch: Current epoch number
        """
        pass

    def on_training_epoch_end(self, epoch, metrics):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
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

    def on_training_epoch_end(self, epoch, metrics: Dict[str, float]):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
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

    def on_training_end(self, metrics: Dict[str, float]):
        """Called at the end of training."""
        if self.early_stop:
            raise RuntimeError(f"Early stopping triggered. Best {self.mode}: {self.best}")

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


class Checkpoint(Callback):
    """Checkpoint saving callback."""

    def __init__(
        self,
        save_path: str = None,
        save_best_only: bool = True,
        save_top_k: int = -1,
        filename: str = None,
        mode: str = 'min',
        every_n_epochs: int = -1,
    ):
        """
        Initialize checkpoint callback.

        Args:
            save_path: Path to save checkpoints
            save_best_only: Only save best model
            save_top_k: Number of best models to save (-1: all)
            filename: Checkpoint filename format
            mode: 'min' or 'max'
            every_n_epochs: Save every n epochs (-1: only when best)
        """
        super().__init__()
        self.save_path = save_path
        self.save_best_only = save_best_only
        self.save_top_k = save_top_k
        self.filename = filename or 'epoch_{epoch}.pt'
        self.mode = mode
        self.every_n_epochs = every_n_epochs

        self.best: Optional[float] = None
        self.best_model_count = 0

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        if self.mode == 'min':
            self.best = float('inf')
        else:
            self.best = float('-inf')

    def on_validation_end(self, metrics: Dict[str, float]):
        """
        Called at the end of validation.

        Args:
            metrics: Validation metrics
        """
        if not self.enabled:
            return

        if self.every_n_epochs > 0 and metrics.get('epoch') % self.every_n_epochs != 0:
            return

        val_metric = metrics.get('val_loss', metrics.get('val_accuracy', metrics.get('eval/metrics', None)))
        if val_metric is None:
            return

        if self.mode == 'min':
            should_save = val_metric < self.best
        else:
            should_save = val_metric > self.best

        if should_save:
            self.best = val_metric
            self.best_model_count += 1

            if self.save_best_only:
                self._save_checkpoint(metrics, f'best_{self.filename}')
            elif self.save_top_k > 0:
                if len([m for m in self._get_all_checkpoints() if 'best_' not in m or m == 'best_']) < self.save_top_k:
                    self._save_checkpoint(metrics, f'best_{self.filename}')
        else:
            if self.save_top_k > 0:
                self._save_checkpoint(metrics, f'epoch_{metrics.get("epoch")}.pt')

    def _save_checkpoint(self, metrics: Dict[str, float], filename: str):
        """Save checkpoint."""
        if self.save_path is None:
            return

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        save_path = os.path.join(self.save_path, filename.format(epoch=metrics.get('epoch', 0)))
        torch.save(self.trainer.model.state_dict(), save_path)

        # Save metrics
        checkpoint_path = os.path.join(self.save_path, filename.replace('.pt', '.json'))
        checkpoint_data = {
            'metrics': metrics,
            'best_model_count': self.best_model_count,
        }
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f)

    def _get_all_checkpoints(self):
        """Get all checkpoint filenames."""
        if self.save_path is None:
            return []

        if not os.path.exists(self.save_path):
            return []

        checkpoints = []
        for f in os.listdir(self.save_path):
            if f.endswith('.pt'):
                checkpoints.append(f)

        return checkpoints

    def state_dict(self):
        """Get state dict."""
        return {
            'save_path': self.save_path,
            'save_best_only': self.save_best_only,
            'save_top_k': self.save_top_k,
            'filename': self.filename,
            'mode': self.mode,
            'every_n_epochs': self.every_n_epochs,
            'best': self.best,
            'best_model_count': self.best_model_count,
        }

    def load_state_dict(self, state_dict):
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
        self.plateau = False

    def setup(self, trainer):
        """Setup callback."""
        super().setup(trainer)
        for param_group in trainer.optimizer.param_groups:
            param_group['lr'] = self.min_lr

    def on_epoch_start(self, epoch):
        """
        Called at the start of each epoch.

        Args:
            epoch: Current epoch number
        """
        self.plateau = False
        self.counter += 1

        if self.counter >= self.patience:
            self.plateau = True

    def on_training_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
        if self.trainer.model.train() == False:
            return

        if self.plateau:
            for param_group in self.trainer.optimizer.param_groups:
                new_lr = max(self.min_lr, param_group['lr'] * self.factor)
                param_group['lr'] = new_lr

            self.counter = 0

    def state_dict(self):
        """Get state dict."""
        return {
            'factor': self.factor,
            'patience': self.patience,
            'min_lr': self.min_lr,
            'counter': self.counter,
            'plateau': self.plateau,
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
    ):
        """
        Initialize model checkpoint.

        Args:
            save_path: Path to save checkpoints
            save_top_k: Number of best models to save
            monitor: Metric to monitor
            mode: 'min' or 'max'
            filename: Checkpoint filename format
        """
        super().__init__()
        self.save_path = save_path
        self.save_top_k = save_top_k
        self.monitor = monitor
        self.mode = mode
        self.filename = filename or 'epoch_{epoch}'

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
        """
        Called at the end of validation.

        Args:
            metrics: Validation metrics
        """
        if not self.enabled:
            return

        val_metric = metrics.get(self.monitor)
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
        """Save checkpoint if we should save."""
        if self.save_path is None:
            return

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        save_path = os.path.join(self.save_path, self.filename.format(epoch=metrics.get('epoch', 0)))
        torch.save(self.trainer.model.state_dict(), save_path)

        # Save metrics
        checkpoint_path = save_path.replace('.pt', '.json')
        checkpoint_data = {
            'metrics': metrics,
            'best': self.best,
        }
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f)

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
        self.writer = SummaryWriter(
            os.path.join(self.log_dir, f'{trainer.get_name()}-{self.name}'),
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

    def on_training_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
        if self.writer is None:
            return

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.writer.add_scalar(f'{key}/{key}', value, epoch)

    def on_training_end(self, metrics: Dict[str, float]):
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

        self.current_step = len(batch) if isinstance(batch, dict) else batch.size(0)

        if (self.current_step - self.last_update) >= self.refresh_rate:
            progress = self.current_step / self.total_steps * 100
            print(f'Epoch {self.epoch}: {self.current_step}/{self.total_steps} ({progress:.1f}%)')
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

    def on_training_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        """
        Called at the end of each epoch.

        Args:
            epoch: Current epoch number
            metrics: Epoch metrics
        """
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
