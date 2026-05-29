"""Training loop and trainer."""

import os
import time
from typing import Dict, Any, Optional, List, Callable, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader

from .metrics import MetricTracker, Metric
from .callbacks import Callback


class Trainer:
    """
    Training loop with callback support.

    The training pipeline:
    - on_training_start
    - for each epoch:
        - on_epoch_start
        - for each batch:
            - on_batch_start
            - forward
            - on_batch_end
            - backward
            - optimizer_step
        - on_epoch_end
    - on_training_end
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer,
        criterion: Optional[nn.Module] = None,
        device: Optional[torch.device] = None,
        train_loader: Optional[DataLoader] = None,
        val_loader: Optional[DataLoader] = None,
        callbacks: Optional[List[Callback]] = None,
        train_batch_size: int = 32,
        val_batch_size: int = 32,
        num_workers: int = 0,
        pin_memory: bool = False,
        enable_progress_bar: bool = False,
    ):
        """
        Initialize trainer.

        Args:
            model: Model to train
            optimizer: Optimizer
            criterion: Loss criterion
            device: Device to use
            train_loader: Training data loader
            val_loader: Validation data loader
            callbacks: List of callbacks
            train_batch_size: Batch size for training
            val_batch_size: Batch size for validation
            num_workers: Num workers for data loading
            pin_memory: Pin memory flag
            enable_progress_bar: Whether to show progress bar
        """
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion or nn.MSELoss()
        self.device = device or (
            torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
        )
        self.train_loader = train_loader
        self.val_loader = val_loader

        self.callbacks = callbacks or []
        for cb in self.callbacks:
            cb.setup(self)

        self.train_batch_size = train_batch_size
        self.val_batch_size = val_batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.enable_progress_bar = enable_progress_bar

        # Training state
        self.epoch = 0
        self.global_step = 0
        self.total_steps = 0

    def get_name(self) -> str:
        """Get trainer name for logging."""
        return self.model.__class__.__name__

    def _move_model(self, mode: str):
        """Move model to device."""
        if mode == 'train':
            self.model.train()
        else:
            self.model.eval()

    def _get_batches(self, loader: DataLoader, shuffle: bool = False):
        """
        Get batches with yield.

        Args:
            loader: Data loader
            shuffle: Whether to shuffle

        Yields:
            batch: Batch data
        """
        loader = loader if loader is not None else self.train_loader
        if loader is None:
            return

        if shuffle:
            loader = DataLoader(
                loader.dataset,
                batch_size=self.train_batch_size,
                shuffle=True,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory,
            )
        else:
            loader = DataLoader(
                loader.dataset,
                batch_size=self.val_batch_size,
                shuffle=False,
                num_workers=self.num_workers,
                pin_memory=self.pin_memory,
            )

        for batch in loader:
            yield batch

    def step(
        self,
        batch: Dict[str, torch.Tensor],
        batch_outputs: Optional[Dict[str, torch.Tensor]] = None,
    ) -> Dict[str, float]:
        """
        Single training step.

        Args:
            batch: Batch inputs
            batch_outputs: Batch outputs (for evaluation)

        Returns:
            Metrics for this step
        """
        metrics = {}

        # Calculate loss
        outputs = self.model(batch)
        loss = self.criterion(outputs, batch.pop('y', batch.pop('target', None)))

        # Backward pass and optimizer step
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()

        # Track metrics
        self.global_step += 1
        metrics = self._update_metrics(loss, batch_outputs, metrics)

        return metrics

    def _update_metrics(
        self,
        loss: torch.Tensor,
        batch_outputs: Optional[Dict[str, torch.Tensor]],
        metrics: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Update and return metrics.

        Args:
            loss: Loss value
            batch_outputs: Batch outputs
            metrics: Current metrics

        Returns:
            Updated metrics
        """
        metrics['loss'] = loss.item()

        if batch_outputs is not None:
            for k, v in batch_outputs.items():
                if isinstance(v, torch.Tensor):
                    metrics[k] = v.mean().item()

        return metrics

    def run(
        self,
        epochs: int = 1,
        verbose: bool = True,
    ) -> Dict[str, List[float]]:
        """
        Run training.

        Args:
            epochs: Number of epochs
            verbose: Whether to print progress

        Returns:
            Training history
        """
        # Track history
        history = {
            'loss': [],
            'val_loss': [],
            'epoch': [],
        }

        # Call training start callback
        for cb in self.callbacks:
            if hasattr(cb, 'on_training_start'):
                cb.on_training_start()

        # Training loop
        for epoch in range(epochs):
            self.epoch = epoch
            self.global_step = 0

            # Call epoch start callback
            epoch_metrics = {}

            # Call epoch start callback
            for cb in self.callbacks:
                if hasattr(cb, 'on_epoch_start'):
                    cb.on_epoch_start(epoch)

            # Training phase
            for step, batch in enumerate(self._get_batches(self.train_loader, shuffle=True)):
                step_metrics = self.step(batch)

                # Call batch end callback
                for cb in self.callbacks:
                    if hasattr(cb, 'on_batch_end'):
                        cb.on_batch_end(step, step_metrics, batch)

                epoch_metrics['loss'] = step_metrics.get('loss', 0.0)
                epoch_metrics['batch'] = step_metrics.get('batch', 0.0)

                # Update metrics tracker
                metric = Metric(
                    name='loss',
                    data=step_metrics.get('loss', 0.0),
                    weights=1,
                )
                self.tracker.update(metric)

            # Call epoch end callback
            for cb in self.callbacks:
                if hasattr(cb, 'on_epoch_end'):
                    cb.on_epoch_end(epoch, epoch_metrics)

            # Validation phase
            if self.val_loader is not None:
                self._move_model('eval')

                val_metrics = self._validate()

                # Call validation end callback
                for cb in self.callbacks:
                    if hasattr(cb, 'on_validation_end'):
                        cb.on_validation_end(val_metrics)

                history['val_loss'].append(val_metrics.get('loss', 0.0))

            # Call epoch end callback with validation metrics
            all_metrics = {**epoch_metrics, **val_metrics}
            for cb in self.callbacks:
                if hasattr(cb, 'on_training_epoch_end'):
                    cb.on_training_epoch_end(epoch, all_metrics)

            if verbose:
                self._print_epoch_metrics(epoch, epoch_metrics, val_metrics)

            history['loss'].append(epoch_metrics.get('loss', 0.0))
            history['epoch'].append(epoch)

        # Call training end callback
        for cb in self.callbacks:
            if hasattr(cb, 'on_training_end'):
                cb.on_training_end(history)

        return history

    def _validate(self) -> Dict[str, float]:
        """
        Run validation.

        Returns:
            Validation metrics
        """
        self.model.eval()
        val_metrics = {}

        with torch.no_grad():
            for batch in self._get_batches(self.val_loader, shuffle=False):
                batch.pop('y', None)
                batch.pop('target', None)

                outputs = self.model(batch)
                loss = self.criterion(outputs, batch.pop('y', batch.pop('target', None)))

                val_metrics['loss'] = loss.item()

        self.model.train()
        return val_metrics

    def _print_epoch_metrics(
        self,
        epoch: int,
        train_metrics: Dict[str, float],
        val_metrics: Dict[str, float],
    ):
        """
        Print epoch metrics.

        Args:
            epoch: Epoch number
            train_metrics: Training metrics
            val_metrics: Validation metrics
        """
        print(f'\nEpoch {epoch + 1}')
        print('=' * 30)
        for k, v in train_metrics.items():
            if isinstance(v, float):
                print(f'{k}: {v:.4f}')
        for k, v in val_metrics.items():
            if isinstance(v, float):
                print(f'{k}: {v:.4f}')
        print('=' * 30 + '\n')

    def state_dict(self) -> Dict[str, Any]:
        """
        Get trainer state dict.

        Returns:
            State dict
        """
        return {
            'model': self.model,
            'optimizer': self.optimizer,
            'criterion': self.criterion,
            'device': self.device,
            'callbacks': [cb.state_dict() for cb in self.callbacks],
            'epoch': self.epoch,
            'global_step': self.global_step,
        }

    def load_state_dict(self, state_dict: Dict[str, Any]):
        """
        Load state dict.

        Args:
            state_dict: State dict to load
        """
        self.model.load_state_dict(state_dict.get('model', {}))
        self.optimizer.load_state_dict(state_dict.get('optimizer', {}))
        self.epoch = state_dict.get('epoch', 0)
        self.global_step = state_dict.get('global_step', 0)
        for i, cb in enumerate(self.callbacks):
            cb.load_state_dict(state_dict['callbacks'][i])

    def save(self, path: str):
        """
        Save trainer state.

        Args:
            path: Path to save to
        """
        torch.save(self.state_dict(), path)

    def load(self, path: str):
        """
        Load trainer state.

        Args:
            path: Path to load from
        """
        state_dict = torch.load(path)
        self.load_state_dict(state_dict)

    @classmethod
    def from_model(
        cls,
        model: nn.Module,
        optimizer,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        epochs: int = 10,
        callbacks: Optional[List[Callback]] = None,
        device: Optional[torch.device] = None,
        train_batch_size: int = 32,
        val_batch_size: int = 32,
    ) -> 'Trainer':
        """
        Create trainer from model.

        Args:
            model: Model to train
            optimizer: Optimizer
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            callbacks: List of callbacks
            device: Device to use
            train_batch_size: Batch size for training
            val_batch_size: Batch size for validation

        Returns:
            Trainer instance
        """
        return cls(
            model=model,
            optimizer=optimizer,
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=epochs,
            callbacks=callbacks,
            device=device,
            train_batch_size=train_batch_size,
            val_batch_size=val_batch_size,
        )
