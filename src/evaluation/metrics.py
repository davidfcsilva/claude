"""Evaluation metrics for ML models."""

from typing import Any


class Accuracy:
    """Accuracy metric."""

    def __init__(self, num_classes: int) -> None:
        """Initialize accuracy metric."""
        self.num_classes = num_classes
        self.correct = 0
        self.total = 0

    def update(self, predictions: list, targets: list) -> None:
        """Update metric with predictions and targets."""
        for pred, target in zip(predictions, targets):
            if pred == target:
                self.correct += 1
            self.total += 1

    def reset(self) -> None:
        """Reset the metric."""
        self.correct = 0
        self.total = 0

    def get_value(self) -> float:
        """Get current accuracy."""
        return self.correct / self.total if self.total > 0 else 0.0


class Loss:
    """Loss tracking metric."""

    def __init__(self) -> None:
        """Initialize loss metric."""
        self.losses: list[float] = []

    def update(self, loss: float) -> None:
        """Record a loss value."""
        self.losses.append(loss)

    def reset(self) -> None:
        """Reset the metric."""
        self.losses.clear()

    def get_value(self) -> float:
        """Get average loss."""
        return sum(self.losses) / len(self.losses) if self.losses else 0.0
