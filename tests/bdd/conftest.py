"""Pytest fixtures for BDD tests."""

import pytest
from src.models.mlp_model import MLPModel
from src.data.base_dataset import TensorDataset
from src.evaluation.metrics import Accuracy, Loss
from src.training.trainer import Trainer


@pytest.fixture
def dummy_config():
    """Return a dummy configuration for testing."""
    return {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 5,
        "weight_decay": 1e-5,
    }


@pytest.fixture
def dummy_model():
    """Return a dummy model instance for testing."""
    return MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)


@pytest.fixture
def dummy_dataset():
    """Return a dummy dataset instance for testing."""
    import torch
    return TensorDataset(
        data=torch.randn(100, 10),
        labels=torch.randint(0, 2, (100,)),
    )


@pytest.fixture
def accuracy_metric():
    """Return an accuracy metric for testing."""
    return Accuracy(num_classes=10)


@pytest.fixture
def loss_metric():
    """Return a loss metric for testing."""
    return Loss()