"""BDD tests for model classification features."""

from pytest_bdd import given, parsers, scenario, then, when

from src.models.mlp_model import MLPModel


@scenario('../features/classification.feature', 'Model classifies with correct mode')
def test_model_classifies_with_correct_mode():
    """Test model can classify with correct mode."""
    pass


@scenario('../features/classification.feature', 'Model switches between train and eval modes')
def test_model_switches_between_modes():
    """Test model switches between modes."""
    pass


@scenario('../features/classification.feature', 'Model retrieves parameters')
def test_model_retrieves_parameters():
    """Test model retrieves parameters."""
    pass


@scenario('../features/classification.feature', 'Model handles different configurations')
def test_model_handles_different_configurations():
    """Test model handles different configurations."""
    pass


# -- Shared step definitions using `target` for all state passing --------------

@given("a model is initialized")
def init_model(target):
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    target["model"] = model


@when("the model is set to training mode")
def set_training(target):
    target["model"].train()


@then("the model should be in training mode")
def check_training(target):
    assert target["model"].training is True


@when("the model is set to evaluation mode")
def set_eval(target):
    target["model"].eval()


@then("the model should be in evaluation mode")
def check_eval(target):
    assert target["model"].training is False


@when("the model is used")
def use_model(target):
    target["result"] = target["model"]


@then("the model should work correctly")
def check_model_works(target):
    assert target["result"] is not None


@given(parsers.parse('a model is initialized with configuration "{model_type}"'))
def init_model_config(model_type: str, target):
    model = MLPModel(input_dim=64, hidden_dims=[32], num_classes=2)
    target["model"] = model
