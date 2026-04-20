Feature: Model Classification Capabilities

  As a data scientist
  I want to verify model can perform classification
  So that I can train classifiers for my ML pipeline

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
    When the model parameters are requested
    Then the model should return the parameters

  Scenario Outline: Model handles different configurations
    Given a model is initialized with configuration "<model_type>"
    When the model is used
    Then the model should work correctly

    Examples:
      | model_type   |
      | classifier   |
      | regressor    |
      | detector     |
