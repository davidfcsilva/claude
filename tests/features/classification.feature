Feature: Model Classification

  Scenario: Model classifies with correct mode
    Given a model is initialized
    When the model is set to training mode
    Then the model should be in training mode

  Scenario: Model switches between train and eval modes
    Given a model is initialized
    When the model is set to training mode
    Then the model should be in training mode
    When the model is set to evaluation mode
    Then the model should be in evaluation mode

  Scenario: Model retrieves parameters
    Given a model is initialized
    When the model is used
    Then the model should work correctly

  Scenario: Model handles different configurations
    Given a model is initialized with configuration "mlp"
    When the model is used
    Then the model should work correctly

