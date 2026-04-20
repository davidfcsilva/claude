Feature: Dataset Handling

  As a data engineer
  I want to verify dataset can be loaded and accessed
  So that I can train models on properly formatted data

  Scenario: Dataset loads with correct length
    Given a dataset is initialized with "<num_samples>" samples
    Then the dataset length should be "<num_samples>"

  Scenario: Dataset retrieves items at index
    Given a dataset is initialized with "<num_samples>" samples
    When an item at index "<index>" is requested
    Then the dataset should return a valid sample

  Scenario Outline: Dataset handles edge indices
    Given a dataset is initialized with "<num_samples>" samples
    When an item at edge index "<index>" is requested
    Then the dataset should handle it gracefully

    Examples:
      | num_samples | index |
      | 100         | 0     |
      | 100         | 99    |
      | 100         | -1    |

  Scenario: Dataset loads from configuration
    Given a dataset is initialized with config
    Then the dataset should load data from config path

  Scenario: Dataset transforms data
    Given a dataset is initialized with transform
    When an item is retrieved
    Then the item should be transformed
