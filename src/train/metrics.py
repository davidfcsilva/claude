"""Metrics for evaluation."""

import torch
from typing import Dict, List, Callable, Optional
from abc import ABC, abstractmethod


class Metric(ABC):
    """Abstract base class for metrics."""

    @abstractmethod
    def __call__(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
        """
        Compute metric.

        Args:
            y_true: Ground truth
            y_pred: Predictions

        Returns:
            Metric value
        """
        pass

    def reset(self):
        """Reset metric state."""
        pass

    def state_dict(self) -> Dict:
        """Get metric state as dict."""
        return {}

    def load_state_dict(self, state: Dict):
        """Load metric state from dict."""
        pass


class AccuracyMetric(Metric):
    """Accuracy metric."""

    def __call__(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
        """
        Compute accuracy.

        Args:
            y_true: Ground truth
            y_pred: Predictions

        Returns:
            Accuracy
        """
        y_pred = y_pred.argmax(dim=1) if y_pred.dim() > 1 else (y_pred > 0.5).float()
        y_true = y_true if y_true.dim() == 1 else y_true.argmax(dim=1)
        return (y_true == y_pred).float().mean().item()


class F1ScoreMetric(Metric):
    """F1 score metric."""

    def __call__(self, y_true: torch.Tensor, y_pred: torch.Tensor, pos: int = 1) -> float:
        """
        Compute F1 score.

        Args:
            y_true: Ground truth
            y_pred: Predictions
            pos: Positive class index

        Returns:
            F1 score
        """
        tp = ((y_true == 1) & (y_pred == pos)).sum().item()
        fp = ((y_true == 0) & (y_pred == pos)).sum().item()
        fn = ((y_true == pos) & (y_pred != pos)).sum().item()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0


class LossMetric(Metric):
    """Loss metric."""

    def __init__(self, loss_fn: Optional[Callable] = None):
        """
        Initialize loss metric.

        Args:
            loss_fn: Loss function
        """
        self.loss_fn = loss_fn or torch.nn.functional.mse_loss

    def __call__(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
        """
        Compute loss.

        Args:
            y_true: Ground truth
            y_pred: Predictions

        Returns:
            Loss
        """
        return self.loss_fn(y_true, y_pred).item()


class MetricTracker:
    """Track metrics over time."""

    def __init__(self):
        """Initialize tracker."""
        self.history: Dict[str, List[float]] = {}
        self.current: Dict[str, float] = {}
        self._metrics: Dict[str, Metric] = {}
        self._compute_fn: Optional[Callable] = None

    def add_metric(self, name: str, metric: Metric):
        """
        Add a metric.

        Args:
            name: Metric name
            metric: Metric instance
        """
        self._metrics[name] = metric
        self.history[name] = []
        self.current[name] = 0.0

    def compute(self, y_true: torch.Tensor, y_pred: torch.Tensor):
        """
        Compute all metrics.

        Args:
            y_true: Ground truth
            y_pred: Predictions
        """
        if self._compute_fn is not None:
            metrics = self._compute_fn(y_true, y_pred)
            for name, value in metrics.items():
                self.history[name].append(value)
                self.current[name] = value
            return

        for name, metric in self._metrics.items():
            value = metric(y_true, y_pred)
            self.history[name].append(value)
            self.current[name] = value

    def compute_one_metric(self, name: str, y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
        """
        Compute one metric.

        Args:
            name: Metric name
            y_true: Ground truth
            y_pred: Predictions

        Returns:
            Metric value
        """
        metric = self._metrics.get(name)
        if metric is None:
            raise ValueError(f"Metric {name} not found")
        return metric(y_true, y_pred)

    def set_compute_fn(self, fn: Callable):
        """
        Set custom compute function.

        Args:
            fn: Compute function
        """
        self._compute_fn = fn

    def get_current(self) -> Dict[str, float]:
        """
        Get current metrics.

        Returns:
            Current metrics dict
        """
        return self.current.copy()

    def get_history(self) -> Dict[str, List[float]]:
        """
        Get history.

        Returns:
            History dict
        """
        return self.history.copy()

    def clear(self):
        """Clear all metrics."""
        self.history.clear()
        self.current.clear()
        self._metrics.clear()
        self._compute_fn = None

    def reset(self):
        """Reset metrics."""
        self.current.clear()
        self._compute_fn = None

    def __call__(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> Dict[str, float]:
        """
        Compute metrics.

        Args:
            y_true: Ground truth
            y_pred: Predictions

        Returns:
            Current metrics
        """
        self.compute(y_true, y_pred)
        return self.current.copy()


def accuracy(
    y_true: torch.Tensor,
    y_pred: torch.Tensor,
    dim: int = 1,
) -> float:
    """
    Compute accuracy.

    Args:
        y_true: Ground truth
        y_pred: Predictions
        dim: Dimension to reduce

    Returns:
        Accuracy
    """
    y_pred = y_pred.argmax(dim=dim) if y_pred.dim() > 1 else (y_pred > 0.5).float()
    y_true = y_true if y_true.dim() == 1 else y_true.argmax(dim=dim)
    return (y_true == y_pred).float().mean().item()


def f1_score(
    y_true: torch.Tensor,
    y_pred: torch.Tensor,
    pos: int = 1,
) -> float:
    """
    Compute F1 score.

    Args:
        y_true: Ground truth
        y_pred: Predictions
        pos: Positive class

    Returns:
        F1 score
    """
    tp = ((y_true == 1) & (y_pred == pos)).sum().item()
    fp = ((y_true == 0) & (y_pred == pos)).sum().item()
    fn = ((y_true == pos) & (y_pred != pos)).sum().item()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
