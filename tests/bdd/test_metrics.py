"""BDD tests for metrics features."""

from pytest_bdd import scenario, given, when, then, parsers
import pytest
from src.metrics.accuracy import Accuracy
from src.metrics.loss import Loss


@scenario('../features/metrics.feature', 'Accuracy metric works correctly')
def test_accuracy_metric():
    """Test accuracy metric."""
    pass


@scenario('../features/metrics.feature', 'Loss metric works correctly')
def test_loss_metric():
    """Test loss metric."""
    pass


@scenario('../features/metrics.feature', 'Metrics can be reset')
def test_metrics_reset():
    """Test metrics reset."""
    pass


@given("an accuracy metric is initialized")
def accuracy_initialized():
    """Given accuracy is initialized."""
    accuracy = Accuracy()
    return accuracy


@when("predictions are made with {accuracy}")
def make_predictions(accuracy: float, accuracy_initialized):
    """When predictions are made."""
    accuracy_initialized.update({"pred": 1, "target": 1})
    return accuracy_initialized


@then("accuracy should be calculated")
def verify_accuracy(accuracy_initialized):
    """Then accuracy should be calculated."""
    score = accuracy_initialized.compute()
    assert score is not None


@scenario('../features/metrics.feature', 'Loss metric works correctly')
def test_loss_calculation():
    """Test loss calculation."""
    pass


@given("a loss metric is initialized")
def loss_initialized():
    """Given loss is initialized."""
    loss = Loss()
    return loss


@when("loss is computed")
def compute_loss(loss_initialized):
    """When loss is computed."""
    loss_initialized.update({"pred": 0.8, "target": 1.0})
    return loss_initialized


@then("loss should be calculated")
def verify_loss(loss_initialized):
    """Then loss should be calculated."""
    score = loss_initialized.compute()
    assert score is not None


@given("accuracy and loss metrics are initialized")
def accuracy_and_loss_initialized():
    """Given metrics are initialized."""
    accuracy = Accuracy()
    loss = Loss()
    return accuracy, loss


@when("the metrics are reset")
def reset_metrics(accuracy_and_loss_initialized):
    """When metrics are reset."""
    accuracy, loss = accuracy_and_loss_initialized
    accuracy.reset()
    loss.reset()
    return accuracy, loss


@then("the metrics should be reset")
def verify_reset(metrics):
    """Then metrics should be reset."""
    assert metrics is not None
