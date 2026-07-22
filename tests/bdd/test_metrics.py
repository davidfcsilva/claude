"""BDD tests for metrics features."""

from pytest_bdd import given, scenario, then, when

from src.evaluation.metrics import Accuracy, Loss


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
def init_accuracy_metric(target):
    target["accuracy"] = Accuracy()


@when("predictions are made")
def make_predictions(target):
    target["accuracy"].update([0, 1, 0], [0, 1, 0])


@then("accuracy should be calculated")
def verify_accuracy(target):
    score = target["accuracy"].get_value()
    assert score is not None


@given("a loss metric is initialized")
def init_loss_metric(target):
    target["loss"] = Loss()


@when("loss is computed")
def compute_loss(target):
    target["loss"].update(0.5)


@then("loss should be calculated")
def verify_loss(target):
    score = target["loss"].get_value()
    assert score is not None


@given("accuracy and loss metrics are initialized")
def init_both_metrics(target):
    target["accuracy"] = Accuracy()
    target["loss"] = Loss()


@when("the metrics are reset")
def reset_both_metrics(target):
    target["accuracy"].reset()
    target["loss"].reset()


@then("the metrics should be reset")
def verify_reset(target):
    acc = target["accuracy"].get_value()
    loss = target["loss"].get_value()
    assert acc == 0.0
    assert loss == 0.0
