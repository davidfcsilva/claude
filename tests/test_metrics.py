"""Tests for evaluation metrics."""

import pytest
from src.evaluation.metrics import Accuracy, Loss


class TestAccuracy:
    """Test cases for Accuracy metric."""

    def test_instantiation(self):
        """Test metric instantiation."""
        acc = Accuracy(num_classes=10)
        assert acc.num_classes == 10

    def test_update(self):
        """Test updating accuracy."""
        acc = Accuracy(num_classes=2)
        acc.update([0, 1, 0], [0, 1, 0])
        assert acc.get_value() == 1.0

    def test_reset(self):
        """Test resetting accuracy."""
        acc = Accuracy(num_classes=2)
        acc.update([0], [1])
        acc.reset()
        assert acc.get_value() == 0.0


class TestLoss:
    """Test cases for Loss metric."""

    def test_instantiation(self):
        """Test metric instantiation."""
        loss = Loss()
        assert loss.losses == []

    def test_update(self):
        """Test updating loss."""
        loss = Loss()
        loss.update(0.5)
        loss.update(0.3)
        assert abs(loss.get_value() - 0.4) < 1e-6

    def test_reset(self):
        """Test resetting loss."""
        loss = Loss()
        loss.update(0.5)
        loss.reset()
        assert loss.get_value() == 0.0
