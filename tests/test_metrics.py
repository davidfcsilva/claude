"""Tests for evaluation metrics."""

import pytest
from src.evaluation.metrics import Accuracy, Loss


class TestAccuracy:
    """Test cases for Accuracy metric."""

    def test_instantiation(self):
        acc = Accuracy(num_classes=10)
        assert acc.num_classes == 10

    def test_update_all_correct(self):
        acc = Accuracy(num_classes=2)
        acc.update([0, 1, 0], [0, 1, 0])
        assert acc.get_value() == 1.0

    def test_update_partial(self):
        acc = Accuracy(num_classes=3)
        acc.update([0, 1, 2, 0], [0, 0, 0, 0])
        assert abs(acc.get_value() - 0.5) < 1e-6

    def test_reset(self):
        acc = Accuracy(num_classes=2)
        acc.update([0], [1])
        acc.reset()
        assert acc.get_value() == 0.0

    def test_empty_get_value(self):
        acc = Accuracy()
        assert acc.get_value() == 0.0


class TestLoss:
    """Test cases for Loss metric."""

    def test_instantiation(self):
        loss = Loss()
        assert loss.get_value() == 0.0

    def test_update_single(self):
        loss = Loss()
        loss.update(0.5)
        assert abs(loss.get_value() - 0.5) < 1e-6

    def test_update_multiple(self):
        loss = Loss()
        loss.update(0.5)
        loss.update(0.3)
        assert abs(loss.get_value() - 0.4) < 1e-6

    def test_reset(self):
        loss = Loss()
        loss.update(0.5)
        loss.reset()
        assert loss.get_value() == 0.0

    def test_steps_counter(self):
        loss = Loss()
        for i in range(5):
            loss.update(float(i))
        assert loss.steps == 5
