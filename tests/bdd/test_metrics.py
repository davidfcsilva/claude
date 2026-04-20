"""BDD tests for evaluation metrics features."""

from pytest_bdd import scenario, given, when, then
import pytest
from src.evaluation.metrics import Accuracy, Loss


@scenario('../features/metrics.feature', 'Accuracy calculates correctly')
def test_accuracy_calculates_correctly():
    """Test accuracy calculates correctly."""
    pass


@scenario('../features/metrics.feature', 'Loss calculates average')
def test_loss_calculates_average():
    """Test loss calculates average."""
    pass


@scenario('../features/metrics.feature', 'Accuracy resets after update')
def test_accuracy_reset_after_update():
    """Test accuracy resets after update."""
    pass


@scenario('../features/metrics.feature', 'Loss resets after update')
def test_loss_reset_after_update():
    """Test loss resets after update."""
    pass


@given('an accuracy metric is initialized with {num_classes} classes')
def accuracy_metric(num_classes: int):
    """Given accuracy metric initialized."""
    return Accuracy(num_classes=num_classes)


@when('{correct} correct and {incorrect} incorrect predictions are made')
def make_predictions(correct: int, incorrect: int, accuracy):
    """When predictions are made."""
    predictions = [0] * (correct + incorrect)
    targets = [0] * correct + [1] * incorrect
    for pred, target in zip(predictions, targets):
        accuracy.update([pred], [target])


@then('the accuracy should be {expected_accuracy}')
def accuracy_check(expected_accuracy: float):
    """Then accuracy should be correct."""
    actual_accuracy = accuracy.get_value()
    assert abs(actual_accuracy - expected_accuracy) < 1e-6


@scenario('../features/metrics.feature', 'Loss calculates average')
def test_loss_average():
    """Test loss average calculation."""
    pass


@given('a loss metric is initialized')
def loss_metric():
    """Given loss metric initialized."""
    return Loss()


@when('losses {loss_values} are recorded')
def record_losses(loss_values_str: str):
    """When losses are recorded."""
    # Parse comma-separated losses
    loss_values = [float(x) for x in loss_values_str.split(',')]
    for loss in loss_values:
        loss_metric().update(loss)


@then('the average loss should be {expected_loss}')
def loss_check(expected_loss: float):
    """Then average loss should be correct."""
    actual_loss = loss_metric().get_value()
    assert abs(actual_loss - expected_loss) < 1e-6


@scenario('../features/metrics.feature', 'Accuracy resets after update')
def test_accuracy_reset():
    """Test accuracy reset."""
    pass


@given('an accuracy metric is initialized')
def accuracy_initialized():
    """Given accuracy metric initialized."""
    return Accuracy(num_classes=10)


@when('predictions are made')
def accuracy_has_value():
    """When predictions are made."""
    accuracy.update([0], [1])


@then('the accuracy metric should have a value')
def accuracy_has_value_check():
    """Then accuracy should have value."""
    value = accuracy_initialized().get_value()
    assert value > 0


@when('the accuracy is reset')
def reset_accuracy():
    """When accuracy is reset."""
    accuracy_initialized().reset()


@then('the accuracy should be 0.0')
def accuracy_reset_check():
    """Then accuracy should be 0."""
    assert accuracy_initialized().get_value() == 0.0


@scenario('../features/metrics.feature', 'Loss resets after update')
def test_loss_reset():
    """Test loss reset."""
    pass


@given('a loss metric is initialized')
def loss_initialized():
    """Given loss metric initialized."""
    return Loss()


@when('losses are recorded')
def loss_has_value():
    """When losses are recorded."""
    loss_initialized().update(0.5)


@then('the loss metric should have a value')
def loss_has_value_check():
    """Then loss should have value."""
    assert loss_initialized().get_value() > 0


@when('the loss is reset')
def reset_loss():
    """When loss is reset."""
    loss_initialized().reset()


@then('the loss should be 0.0')
def loss_reset_check():
    """Then loss should be 0."""
    assert loss_initialized().get_value() == 0.0
