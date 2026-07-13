Feature: Training

  Scenario: Model trains on dataset
    Given a model and dataset are provided
    When the model is trained for 1 epochs
    Then the model should be trained

  Scenario: Trainer handles epochs correctly
    Given a trainer is configured
    When the training is run
    Then the metrics should be reported

  Scenario: Trainer can save and load checkpoints
    Given a trainer is configured on "cpu"
    When the training completes
    Then the trainer should be saved

  Scenario: Trainer calculates and reports metrics
    Given a trainer is configured with metrics "accuracy,loss"
    When the training is executed
    Then the metrics should be calculated
