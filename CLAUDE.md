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

## Commit Guardrails

### Only Commit Complete, Working Changes
- **Never commit mid-change.** A commit is a unit of completed work — all files for that change are written, tested (if applicable), and ready. Partial commits fragment history and make rollbacks dangerous.
- **Verify before committing.** If the change involves code, run the relevant tests or build step first. Don't commit broken state.
- **Don't commit to "save progress."** Use stashes (`git stash`) or uncommitted working-tree changes for in-progress work.

### Always Commit to `development`
- **Commit on feature branches only.** Feature branches fork from `development`; merge back to `development` via PR. Never commit directly to `main`.
- **Before committing, confirm the branch.** If you're not on a feature branch or `development`, stop and clarify — do not force-push to `main` or amend `main`.
- **Merge path:** `feat/*` → PR → squash-merge into `development` → PR → `main`. The only way code reaches `main` is through a reviewed PR from `development`.

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

## Task Completion Rule

### Push to `origin development` After Completing All Tasks
- **Always push after finishing.** Once every task in the current session is complete — all changes committed, tested, and verified — push the code to `origin development`.
- **Never skip the push.** Completed work stays local until pushed. Unpushed commits are at risk of being lost and invisible to the team.
- **Push before ending the session.** If multiple tasks were requested and all are done, the final step is always:

```bash
git push origin development
```

- **If on a feature branch,** push that feature branch instead, then ensure it's merged into `development` via PR before considering the work complete.

## Spec-Driven Development

### Spec File: `argocddemo-spec.yaml`
- **Single source of truth.** All definitions for the argocddemo application live in `argocddemo-spec.yaml` at the repository root. Before making any change to the application, read this file to understand what currently exists.
- **Update the spec before implementing.** When adding or modifying components (endpoints, resources, config values, services), update the spec first, then implement the Kubernetes manifests and source code to match.
- **Verify against the spec.** After deploying a change, confirm the live state matches the spec by checking endpoints, resource limits, probe configs, and service topology.

### Validate argocddemo Changes Against the Spec
- **Mandatory validation step.** After committing any change inside `argocddemo/`, validate that the live deployed state matches `argocddemo-spec.yaml` before considering the work complete. This is non-negotiable — a commit is not "done" until verified against the spec.
- **Validation checklist per change:**
  - Read `argocddemo-spec.yaml` to identify every field affected by the change.
  - Wait for ArgoCD to sync the new manifests.
  - Hit each backend endpoint listed in the spec via `192.168.51.206` and confirm the live response matches the spec's `example_response`.
  - Verify pod status (`kubectl get pods -n argocddemo`) — all replicas must be Running and Ready per the spec's `replicas` count.
  - Verify service status (`kubectl get svc frontend -n argocddemo`) — type, port, and LoadBalancer IP match the spec.
  - If probes were changed, confirm they fire against the correct path/port by checking pod events (`kubectl describe pods <pod> -n argocddemo`).
- **If the live state does not match the spec,** diagnose and fix the mismatch before pushing. Do not push a commit that breaks spec compliance.
- **Update the spec first.** If the change intentionally modifies behaviour, update `argocddemo-spec.yaml` to reflect the new desired state, then implement and verify against that updated spec.

### Application Access
- The argocddemo frontend LoadBalancer is reachable at **192.168.51.206** (hardcoded on the user's cluster). Use this IP to verify the application is running, test endpoints, or check live behavior after deploying changes.

