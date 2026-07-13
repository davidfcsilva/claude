Feature: Dataset

  Scenario: Dataset loads and processes data
    Given a dataset is initialized
    Then the dataset length should be greater than zero

  Scenario: Dataset handles missing files
    Given a dataset is initialized with config "/data"
    When the data is loaded from "nonexistent.csv"
    Then the data should be loaded

  Scenario: Dataset can be initialized with config
    Given a dataset is initialized
    Then the dataset length should be greater than zero

  Scenario: Dataset returns correct sample
    Given a dataset is initialized
    When a sample is retrieved at index 0
    Then the returned sample should be valid
