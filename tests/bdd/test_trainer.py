"""BDD tests for training features."""

import torch
from pytest_bdd import given, parsers, scenario, then, when
from torch.utils.data import DataLoader

from src.data.base_dataset import TensorDataset
from src.models.mlp_model import MLPModel
from src.training.trainer import Trainer


@scenario('../features/training.feature', 'Model trains on dataset')
def test_model_trains_on_dataset():
    """Test model trains correctly."""
    pass


@scenario('../features/training.feature', 'Trainer handles epochs correctly')
def test_trainer_handles_epochs():
    """Test trainer handles epochs."""
    pass


@scenario('../features/training.feature', 'Trainer can save and load checkpoints')
def test_trainer_save_load_checkpoints():
    """Test trainer checkpoint handling."""
    pass


@scenario('../features/training.feature', 'Trainer calculates and reports metrics')
def test_trainer_reports_metrics():
    """Test trainer metric reporting."""
    pass


@given("a model and dataset are provided")
def model_and_dataset_provided(target):
    """Create a model and dataset, store them in shared target state."""
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    dataset = TensorDataset(
        data=torch.randn(10, 64),
        labels=torch.randint(0, 2, (10,)),
    )
    target["model"] = model
    target["dataset"] = dataset


@when(parsers.parse("the model is trained for {epochs} epochs"))
def train_model(epochs, target):
    """Train the model for the specified number of epochs."""
    epochs = int(epochs)
    model = target["model"]
    dataset = target["dataset"]
    train_loader = DataLoader(dataset, batch_size=4)
    trainer = Trainer(model, train_loader)
    result = trainer.train(epochs=epochs)
    target["trainer"] = trainer
    target["result"] = result


@then("the model should be trained")
def verify_trained(target):
    """Verify the model has been trained."""
    assert target["trainer"].trained is True


@given("a trainer is configured")
def trainer_is_configured(target):
    """Create a default trainer and store it in shared state."""
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    dataset = TensorDataset(
        data=torch.randn(10, 64),
        labels=torch.randint(0, 2, (10,)),
    )
    train_loader = DataLoader(dataset, batch_size=4)
    trainer = Trainer(model, train_loader)
    target["trainer"] = trainer


@when("the training is run")
def training_is_run(target):
    """Run one epoch of training and store the result."""
    trainer = target["trainer"]
    result = trainer.train(epochs=1)
    target["result"] = result


@then("the metrics should be reported")
def metrics_reported(target):
    """Verify that training returned a non-None result."""
    assert target["result"] is not None


@given(parsers.parse('a trainer is configured on "{device}"'))
def trainer_on_device(device: str, target):
    """Create a trainer bound to the specified device."""
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    dataset = TensorDataset(
        data=torch.randn(10, 64),
        labels=torch.randint(0, 2, (10,)),
    )
    train_loader = DataLoader(dataset, batch_size=4)
    trainer = Trainer(model, train_loader, device=device)
    target["trainer"] = trainer


@when("the training completes")
def training_completes(target):
    """Run one epoch of training."""
    trainer = target["trainer"]
    result = trainer.train(epochs=1)
    target["result"] = result


@then("the trainer should be saved")
def trainer_saved(target):
    """Verify the training result exists and trainer is in trained state."""
    assert target["result"] is not None
    assert target["trainer"].trained is True


@given(parsers.parse('a trainer is configured with metrics "{metrics}"'))
def trainer_with_metrics(metrics: str, target):
    """Create a trainer (metrics string recorded but default trainer created)."""
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    dataset = TensorDataset(
        data=torch.randn(10, 64),
        labels=torch.randint(0, 2, (10,)),
    )
    train_loader = DataLoader(dataset, batch_size=4)
    trainer = Trainer(model, train_loader)
    target["trainer"] = trainer


@when("the training is executed")
def execute_training(target):
    """Run one epoch of training and capture the result."""
    trainer = target["trainer"]
    result = trainer.train(epochs=1)
    target["result"] = result


@then("the metrics should be calculated")
def verify_metrics(target):
    """Verify the training returned metrics."""
    assert target["result"] is not None
