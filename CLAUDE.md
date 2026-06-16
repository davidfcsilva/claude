# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a machine learning project with a modular architecture designed for reproducible experiments. The project uses PyTorch as the primary deep learning framework with scikit-learn for traditional ML tasks.

## Project Structure

```
.
├── src/
│   ├── models/          # Model definitions (base_model.py)
│   ├── data/            # Data loading and preprocessing (base_dataset.py)
│   ├── training/        # Training scripts (train.py)
│   └── evaluation/      # Evaluation metrics (metrics.py)
├── tests/
│   └── unit/            # Unit tests for components
├── config/              # YAML configuration files
├── experiments/         # MLflow experiment logs
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── Makefile             # Common commands
└── .gitignore           # Git ignore patterns
```

## Common Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest
# or run a single test file:
pytest tests/test_base_model.py -v
```

### Train Model
```bash
python src/training/train.py --config config/default_config.yaml
```

### Run All Commands via Make
```bash
make install    # Install dependencies
make test       # Run all tests
make train      # Train the model
make clean      # Clean generated files
```

## Architecture Details

### Model Layer (`src/models/`)
- **BaseModel**: Abstract base class defining the interface for all models
  - `forward()`: Perform forward pass
  - `train()`: Set model to training mode
  - `eval()`: Set model to evaluation mode
  - `get_params()`: Get model parameters

### Data Layer (`src/data/`)
- **BaseDataset**: Abstract base class for all datasets
  - `__len__()`: Return number of samples
  - `__getitem__()`: Get item at index

### Training Layer (`src/training/`)
- **BaseTrainer**: Abstract base class for training pipelines
  - `train_epoch()`: Train for one epoch
  - `evaluate()`: Evaluate model
  - `save_checkpoint()`: Save model checkpoint
  - `load_checkpoint()`: Load model checkpoint

### Evaluation Layer (`src/evaluation/`)
- **Accuracy**: Classification accuracy metric
- **Loss**: Loss tracking metric

### Configuration (`config/`)
- **default_config.yaml**: Training hyperparameters (learning rate, batch size, epochs, etc.)
- MLflow settings for experiment tracking
- Device configuration (cpu/cuda)

## Testing Strategy

- Unit tests in `tests/` directory
- Test fixtures in `conftest.py` if needed
- Coverage reports with `pytest-cov`
- Run with: `pytest tests/ -v --cov=src`

## Environment Variables

```bash
export HF_HOME=~/.cache/huggingface
export TORCH_HOME=~/.cache/torch
```

## MLflow Integration

Experiments are logged to `./mlruns/` with tracking URI configured in `config/default_config.yaml`.

## Branching & Merge Workflow

### Branch Model
```
main              ← production-ready, protected branch
development       ← integration branch for all work-in-progress
feat/description  ← feature branches always fork from development
```

### Creating a Feature Branch
```bash
git checkout development
git pull origin development
git checkout -b feat/short-description
```

### Working on a Feature
1. Commit frequently with conventional commit messages (`feat/`, `fix/`, `chore/`, `docs/`, `refactor/`).
2. Stage only the files you intentionally changed (e.g., `git add CLAUDE.md` or `git add src/models/*.py`).

### Creating a Pull Request (development → main)

```bash
# Push your feature branch
git push -u origin feat/short-description

# Create a draft PR first so it's visible early
gh pr create --base main --head feat/short-description --draft \
  --title "feat: <brief description>" \
  --body "## What
<summary of changes>

## Checklist
- [ ] Tests pass
- [ ] No lint errors
- [ ] Self-reviewed my own code

🤖 Generated with Claude Code"
```

### Completing the PR (Merging to main)

1. **Ensure tests pass:** `pytest` and fix any failures on your branch.
2. **Mark the PR as ready:** `gh pr ready <pr-number>`
3. **Request review** if working in a team, or self-review if solo.
4. **Squash-merge once approved:** `gh pr merge <pr-number> --squash --auto`

### If main moves while you're working
```bash
git checkout development
git pull origin development
git checkout feat/short-description
git rebase development   # or merge, whichever you prefer
# Resolve conflicts if any, then force-push: git push --force-with-lease
```
