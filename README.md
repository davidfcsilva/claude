# ML Project

Machine learning project with reproducible experiments and model training pipelines.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start training
python train.py
```

## Project Structure

```
src/
├── data/          # Data loading scripts
├── models/        # Model definitions
├── training/      # Training scripts
└── evaluation/    # Evaluation metrics
tests/
├── unit/          # Unit tests
└── integration/   # Integration tests
experiments/       # MLflow experiment logs
config/            # Configuration files
```

## Environment Variables

```bash
export HF_HOME=~/.cache/huggingface
export TORCH_HOME=~/.cache/torch
```
