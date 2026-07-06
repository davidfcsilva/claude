"""Evaluation metrics for ML models."""

from collections import deque
from typing import Sequence


class Accuracy:
    """Classification accuracy metric."""

    def __init__(self, num_classes: int = 10) -> None:
        """Initialize accuracy metric.

        Args:
            num_classes: Number of output classes.
        """
        self.num_classes = num_classes
        self.correct = 0
        self.total = 0

    def update(self, predictions: Sequence[int], targets: Sequence[int]) -> None:
        """Update metric with a batch of predictions and targets."""
        correct = sum(1 for pred, target in zip(predictions, targets) if pred == target)
        self.correct += correct
        self.total += len(predictions)

    def reset(self) -> None:
        """Reset the metric counters."""
        self.correct = 0
        self.total = 0

    def get_value(self) -> float:
        """Get current accuracy value in [0, 1]."""
        return self.correct / self.total if self.total > 0 else 0.0


class Loss:
    """Running average loss tracking metric."""

    def __init__(self, max_history: int = 10_000) -> None:
        """Initialize loss metric.

        Args:
            max_history: Maximum number of loss values to retain in memory.
        """
        self._losses: deque[float] = deque(maxlen=max_history)
        self._running_sum: float = 0.0
        self._count: int = 0

    def update(self, loss_value: float) -> None:
        """Record a single loss value."""
        if self._losses.maxlen and len(self._losses) == self._losses.maxlen:
            self._running_sum -= self._losses[0]
        self._losses.append(loss_value)
        self._running_sum += loss_value
        self._count += 1

    def reset(self) -> None:
        """Reset the metric."""
        self._losses.clear()
        self._running_sum = 0.0
        self._count = 0

    def get_value(self) -> float:
        """Get average of stored loss values."""
        return self._running_sum / len(self._losses) if self._losses else 0.0

    @property
    def steps(self) -> int:
        """Total number of updates ever called."""
        return self._count
