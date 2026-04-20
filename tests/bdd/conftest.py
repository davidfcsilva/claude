"""Pytest fixtures for BDD tests."""

import pytest
from src.models.base_model import BaseModel
from src.data.base_dataset import BaseDataset
from src.evaluation.metrics import Accuracy, Loss
from src.training.base_trainer import BaseTrainer


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
    return BaseModel(config={"model_type": "dummy", "hidden_size": 128})


@pytest.fixture
def dummy_dataset():
    """Return a dummy dataset instance for testing."""
    return BaseDataset(config={"data_path": "dummy_path", "transform": None})


@pytest.fixture
def dummy_trainer(dummy_model, dummy_dataset):
    """Return a dummy trainer instance for testing."""
    return BaseTrainer(
        model=dummy_model,
        dataset=dummy_dataset,
        config={"device": "cpu"}
    )


@pytest.fixture
def accuracy_metric():
    """Return an accuracy metric for testing."""
    return Accuracy(num_classes=10)


@pytest.fixture
def loss_metric():
    """Return a loss metric for testing."""
    return Loss()
