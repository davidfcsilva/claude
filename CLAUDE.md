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

## Operational Skills

### git-vcs (`/vcs`)

When the user asks to manage version control — commit, branch, push, merge, rebase, resolve conflicts, inspect history, stash, tag, or reset — use the `/vcs` slash-command. It wraps all git operations with built-in branch protection (refuses destructive ops on `main`/`master`) and conventional commit enforcement.

```
/vcs status                                    → working tree status + branch info
/vcs commit feat "add pagination to listings"  → stage all, commit with conventional type
/vcs branch create feat/user-auth              → create and switch to new branch
/vcs merge development                         → merge into current branch
/vcs conflict status                           → show files with unresolved conflicts
/vcs conflict resolve src/app.py theirs         → accept incoming for a conflicted file
/vcs push                                      → push with auto-tracking setup
/vcs pull --rebase                             → pull, rebasing local commits
/vcs tree -L 10 --all                          → commit graph for all branches
/vcs log --feat -n 5                           → last 5 feature commits
/vcs info                                      → repo summary (remote, ahead/behind)
```

Source: `bin/git-vcs` (executable bash script). Skill definition: `.claude/skills/git-vcs/SKILL.md`.

### k8s-troubleshoot (`/k8s`)

When the argocddemo app is broken or needs debugging, use the `/k8s` slash-command. It wraps kubectl with argocddemo defaults and auto-discovers pods so you don't need to type namespace or pod names manually.

```
/k8s logs                      → tail 100 lines from the first matching pod
/k8s logs -n 500 --follow      → follow last 500 lines in real-time
/k8s describe backend-f4abc    → full pod spec + recent events for a specific pod
/k8s exec curl http://localhost:8000/health   → run curl inside the auto-discovered pod
/k8s port-forward backend 8080:8000            → expose service on localhost:8080
```

Source: `bin/k8s-troubleshoot` (executable bash script, zero external interpreter dependencies). Skill definition: `.claude/skills/k8s-troubleshoot/SKILL.md`.

## Branching & Merge Workflow

### Branch Model
```
main              ← production-ready, protected branch
development       ← integration branch for all work-in-progress
feat/description  ← feature branches always fork from development
```

### Creating a Feature Branch
```bash
/vcs branch switch development
/vcs pull --rebase
/vcs branch create feat/short-description
```

### Working on a Feature
1. Commit frequently with conventional commit messages using `/vcs commit <type> <message>` (types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `ci`).
2. Stage only the files you intentionally changed before committing (use `/vcs diff` to review what's about to be committed).

## Commit Guardrails

### Only Commit Complete, Working Changes
- **Never commit mid-change.** A commit is a unit of completed work — all files for that change are written, tested (if applicable), and ready. Partial commits fragment history and make rollbacks dangerous.
- **Verify before committing.** If the change involves code, run the relevant tests or build step first. Don't commit broken state.
- **Don't commit to "save progress."** Use stashes (`/vcs stash save`) or uncommitted working-tree changes for in-progress work.

### Always Commit to `development`
- **Commit on feature branches only.** Feature branches fork from `development`; merge back to `development` via PR. Never commit directly to `main`.
- **Before committing, confirm the branch.** If you're not on a feature branch or `development`, stop and clarify — do not force-push to `main` or amend `main`.
- **Merge path:** `feat/*` → PR → squash-merge into `development` → PR → `main`. The only way code reaches `main` is through a reviewed PR from `development`.

### Creating a Pull Request (development → main)

```bash
# Push your feature branch
/vcs push

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
/vcs branch switch development
/vcs pull --rebase
/vcs branch switch feat/short-description
/vcs rebase development
# If conflicts: /vcs conflict status, /vcs conflict resolve <file> <mode>, /vcs conflict continue
```

## Task Completion Rule

### Push to `origin development` After Completing All Tasks
- **Always push after finishing.** Once every task in the current session is complete — all changes committed, tested, and verified — push the code to `origin development`.
- **Never skip the push.** Completed work stays local until pushed. Unpushed commits are at risk of being lost and invisible to the team.
- **Push before ending the session.** If multiple tasks were requested and all are done, the final step is always:

```bash
/vcs push
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

