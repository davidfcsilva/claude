# ML Project Terminal Instructions

This document provides a comprehensive guide to the available commands and options for working with this machine learning project.

## Project Overview

This is a machine learning project with a modular architecture designed for reproducible experiments. The project uses PyTorch as the primary deep learning framework with scikit-learn for traditional ML tasks.

## Available Commands

### Makefile Commands
The project uses a Makefile with the following commands:

- `make install` - Install all project dependencies including:
  - Core ML libraries (numpy, pandas, scikit-learn)
  - Deep learning frameworks (torch, torchvision, transformers)
  - MLOps tools (mlflow, optuna, pytorch-lightning)
  - Testing frameworks (pytest, pytest-cov, pytest-bdd)
  - Agent development tools (langchain, langchain-community, langchain-openai)

- `make test` - Run all unit tests in the tests/ directory

- `make bdd-test` - Run BDD (Behavior Driven Development) tests in the tests/bdd/ directory with coverage reporting

- `make train` - Train the model using the default configuration

- `make clean` - Clean generated files including:
  - Python cache files (__pycache__)
  - .pyc files
  - pytest cache directories
  - .cache directories

### Direct Python Commands

- `python src/training/train.py` - Run the main training script with default configuration

### Environment Variables

The project requires these environment variables to be set:
- `HF_HOME=~/.cache/huggingface`
- `TORCH_HOME=~/.cache/torch`

## Project Structure

```
.
├── src/                 # Source code
│   ├── models/          # Model definitions
│   ├── data/            # Data loading and preprocessing
│   ├── training/        # Training scripts
│   └── evaluation/      # Evaluation metrics
├── tests/               # Test files
│   ├── unit/            # Unit tests
│   └── bdd/             # BDD tests
├── config/              # Configuration files
├── experiments/         # MLflow experiment logs
├── examples/            # LangChain agent examples
├── Makefile             # Build commands
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Examples

The examples directory contains LangChain agent examples:

### Simple Research Agent
- File: `examples/langchain_agent_example.py`
- Run: `python examples/langchain_agent_example.py`
- Can be run interactively or with specific queries:
  `python examples/langchain_agent_example.py <<< "What's the capital of France?"`

### Multi-Agent Team
- File: `examples/multi_agent_example.py`
- Run: `python examples/multi_agent_example.py`

## Testing

### Unit Tests
Run all unit tests:
```bash
pytest tests/
```

Run a specific test file:
```bash
pytest tests/test_base_model.py -v
```

### BDD Tests
Run BDD tests with coverage:
```bash
pytest tests/bdd/ -v --cov=src
```

## Configuration

Configuration files are located in the `config/` directory:
- `default_config.yaml` - Main training hyperparameters (learning rate, batch size, epochs, etc.)
- MLflow settings for experiment tracking
- Device configuration (cpu/cuda)

## MLflow Integration

Experiments are logged to `./mlruns/` with tracking URI configured in `config/default_config.yaml`.

## Setup Instructions

1. Install dependencies:
   ```bash
   make install
   ```

2. Run tests:
   ```bash
   make test
   ```

3. Start training:
   ```bash
   make train
   ```

## Development Tips

- Use `make clean` to clear cache files when encountering import issues
- Set environment variables as specified in the documentation
- Run specific tests to debug issues quickly
- Use the Makefile for consistent command execution across the team