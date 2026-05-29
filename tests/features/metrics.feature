Feature: Metrics

  Scenario: Accuracy metric works correctly
    Given an accuracy metric is initialized
    When predictions are made
    Then accuracy should be calculated

  Scenario: Loss metric works correctly
    Given a loss metric is initialized
    When loss is computed
    Then loss should be calculated

  Scenario: Metrics can be reset
    Given accuracy and loss metrics are initialized
    When the metrics are reset
    Then the metrics should be reset
