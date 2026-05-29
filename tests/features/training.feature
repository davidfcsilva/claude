Feature: Training

  Scenario: Trainer is initialized with model and dataset
    Given a trainer is initialized
    When the trainer is accessed
    Then the trainer should have model and dataset

  Scenario: Trainer handles configuration
    Given a trainer is initialized with config
    When the trainer is accessed
    Then the trainer should have model and dataset
