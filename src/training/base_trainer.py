"""Base trainer class for all training pipelines."""

import abc
from typing import Any


class BaseTrainer(abc.ABC):
    """Abstract base class for all trainers."""

    def __init__(self, model, dataset, config: dict[str, Any] | None = None):
        """Initialize the trainer."""
        self.model = model
        self.dataset = dataset
        self.config = config or {}

    @abc.abstractmethod
    def train_epoch(self) -> dict[str, float]:
        """Train for one epoch."""
        pass

    @abc.abstractmethod
    def evaluate(self) -> dict[str, float]:
        """Evaluate the model."""
        pass

    def save_checkpoint(self, path: str) -> None:
        """Save model checkpoint."""
        import torch
        torch.save(self.model.get_params(), path)

    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint."""
        import torch
        self.model.set_params(torch.load(path))
