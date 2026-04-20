Feature: Training Pipeline

  As a ML engineer
  I want to verify the training pipeline works correctly
  So that I can train models end-to-end

  Scenario: Trainer trains for one epoch
    Given a trainer is initialized with model and dataset
    When the trainer trains one epoch
    Then the trainer should complete training

  Scenario: Trainer evaluates the model
    Given a trainer is initialized
    When the trainer evaluates
    Then the trainer should return evaluation metrics

  Scenario: Trainer saves checkpoint
    Given a trainer is initialized
    When the checkpoint is saved with path "<checkpoint_path>"
    Then the checkpoint should be saved

  Scenario: Trainer loads checkpoint
    Given a trainer is initialized
    Given a checkpoint is saved
    When the checkpoint is loaded from "<checkpoint_path>"
    Then the trainer should load the checkpoint

  Scenario Outline: Trainer handles different epochs
    Given a trainer is initialized
    When the trainer trains "<num_epochs>" epochs
    Then the trainer should complete training

    Examples:
      | num_epochs |
      | 1          |
      | 10         |
      | 100        |

  Scenario: Trainer uses correct device
    Given a trainer is initialized with device "<device>"
    When training starts
    Then the trainer should use the specified device

    Examples:
      | device   |
      | cpu      |
      | cuda:0   |
      | auto     |
