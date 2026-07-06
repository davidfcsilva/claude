"""Base trainer class for all training pipelines."""

import abc
from typing import Any


class BaseTrainer(abc.ABC):
    """Abstract base class for all trainers."""

    def __init__(self, model: Any, dataset: Any, config: dict[str, Any] | None = None):
        """Initialize the trainer.

        Args:
            model: The model to train (should have get_params/set_model_params methods).
            dataset: The dataset to train on.
            config: Optional training configuration dictionary.
        """
        self.model = model
        self.dataset = dataset
        self.config = config or {}

    @abc.abstractmethod
    def train_epoch(self) -> dict[str, float]:
        """Train for one epoch."""
        ...

    @abc.abstractmethod
    def evaluate(self) -> dict[str, float]:
        """Evaluate the model."""
        ...

    def save_checkpoint(self, path: str) -> None:
        """Save model checkpoint to disk."""
        import torch
        torch.save(self.model.get_params(), path)

    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint from disk."""
        import torch
        state = torch.load(path, weights_only=True)
        self.model.set_model_params(state)
