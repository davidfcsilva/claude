Feature: Dataset

  Scenario: Dataset is initialized with configuration
    Given a dataset is initialized
    When the dataset is accessed
    Then the dataset should return correct length

  Scenario: Dataset handles configuration
    Given a dataset is initialized with config path "/data"
    When the dataset is accessed
    Then the dataset should return correct length
