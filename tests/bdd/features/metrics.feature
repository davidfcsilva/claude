Feature: Evaluation Metrics

  As a data scientist
  I want to verify metrics calculate correctly
  So that I can evaluate model performance

  Scenario: Accuracy calculates correctly
    Given an accuracy metric is initialized with "<num_classes>" classes
    When "<correct>" correct and "<incorrect>" incorrect predictions are made
    Then the accuracy should be "<expected_accuracy>"

    Examples:
      | num_classes | correct | incorrect | expected_accuracy |
      | 10          | 8       | 2         | 0.8               |
      | 10          | 10      | 0         | 1.0               |
      | 10          | 0       | 10        | 0.0               |
      | 10          | 5       | 5         | 0.5               |

  Scenario: Loss calculates average
    Given a loss metric is initialized
    When losses "<loss_values>" are recorded
    Then the average loss should be "<expected_loss>"

    Examples:
      | loss_values  | expected_loss |
      | 0.1, 0.2     | 0.15          |
      | 0.5, 0.5     | 0.5           |
      | 0.0, 1.0     | 0.5           |

  Scenario: Accuracy resets after update
    Given an accuracy metric is initialized
    When predictions are made
    Then the accuracy metric should have a value
    When the accuracy is reset
    Then the accuracy should be 0.0

  Scenario: Loss resets after update
    Given a loss metric is initialized
    When losses are recorded
    Then the loss metric should have a value
    When the loss is reset
    Then the loss should be 0.0
