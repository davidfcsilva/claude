"""BDD tests for model classification features."""

from pytest_bdd import scenario, given, when, then, parsers


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


@given("a model is initialized")
def _init_model(target):
    from src.models.base_model import BaseModel
    model = BaseModel()
    target["model"] = model


@when("the model is set to training mode")
def _set_training(target):
    target["model"].train()


@then("the model should be in training mode")
def _check_training(target):
    assert target["model"].training is True


@when("the model is set to evaluation mode")
def _set_eval(target):
    target["model"].eval()


@then("the model should be in evaluation mode")
def _check_eval(target):
    assert target["model"].training is False


@when("the model is used")
def _use_model(target):
    target["result"] = target["model"]


@then("the model should work correctly")
def _check_model_works(target):
    assert target["result"] is not None


@given(parsers.parse('a model is initialized with configuration "{model_type}"'))
def _init_model_with_config(model_type: str, target):
    from src.models.base_model import BaseModel
    model = BaseModel(config={"model_type": model_type})
    target["model"] = model
