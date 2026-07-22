# Backlog

Generated: 2026-07-01 | Source: Full repository audit

---

## CRITICAL — Security & Data Loss

### C-1: OpenAI API key committed to repository
- **Files:** `.env` (line 1)
- **Problem:** A full, active OpenAI project API key (`sk-proj-...`) is stored in plaintext. Despite `.env` being in `.gitignore`, this file exists in the working tree and may already be in git history.
- **Impact:** Anyone with repo access can use the key against your billing account. If pushed to a remote, it's exposed publicly.
- **Fix:** Rotate the key immediately on OpenAI. Purge from git history with `git filter-repo`. Switch to environment injection or a secrets manager.

### C-2: Training entry point is fundamentally broken
- **Files:** `src/training/train.py` (lines 21–35), `src/models/base_model.py`, `src/data/base_dataset.py`, `src/training/base_trainer.py`
- **Problem:** `train.py` tries to instantiate abstract base classes (`BaseModel`, `BaseDataset`, `BaseTrainer`). Python's `abc` module prevents this — it raises `TypeError: Can't instantiate abstract class...`. The entire training pipeline cannot run.
- **Impact:** `make train` and `python src/training/train.py --config ...` both crash immediately. The project is non-functional as documented.
- **Fix:** Either implement concrete subclasses and use them in `train.py`, or switch to the working `src/train/trainer.py` implementation which uses real PyTorch `nn.Module` objects.

### C-3: BaseModel crashes on train()/eval() — `_training` never initialized
- **Files:** `src/models/base_model.py` (lines 18–24)
- **Problem:** `__init__` never sets `self._training`. The `train()` method does `self._training = True`, so the first call works. But `eval()` does `self._training = False` which also works. However, nothing reads `_training`, and if any subclass checks `self._training` in `__init__` or before calling `train()`, it gets `AttributeError`.
- **Impact:** Silent bug — `_training` attribute exists after first method call but not at construction. Any code that checks training state early will crash.
- **Fix:** Add `self._training = False` to `__init__`.

### C-4: BaseTrainer.load_checkpoint() calls non-existent `set_params()`
- **Files:** `src/training/base_trainer.py` (line 34)
- **Problem:** Calls `self.model.set_params(torch.load(path))`, but `BaseModel` only defines `get_params()`. There is no `set_params()` method anywhere.
- **Impact:** `AttributeError: 'BaseModel' object has no attribute 'set_params'` on every checkpoint load.
- **Fix:** Add `set_params()` to `BaseModel`, or use the correct PyTorch pattern (`model.load_state_dict()`).

---

## HIGH — Architecture & Correctness

### H-1: Duplicate training frameworks (`src/training/` vs `src/train/`)
- **Files:** `src/training/` (2 files) vs `src/train/` (9 files)
- **Problem:** The repo has two parallel training systems:
  - `src/training/` — abstract base classes (broken, see C-2)
  - `src/train/` — full PyTorch implementation with Trainer, callbacks, metrics, losses, config loading, data utilities
- CLAUDE.md only documents `src/training/`. The `src/train/` directory is completely undocumented.
- **Impact:** Developers don't know which to use. The documented path doesn't work. The working code is invisible.
- **Fix:** Consolidate to one system. `src/train/trainer.py` is the substantially complete implementation — migrate documentation and either delete `src/training/` or make it a compatibility layer.

### H-2: Duplicate metrics implementations
- **Files:** `src/train/metrics.py` vs `src/evaluation/metrics.py`
- **Problem:** Two separate metric systems exist:
  - `src/evaluation/metrics.py` — simple functions (accuracy, loss) per CLAUDE.md spec
  - `src/train/metric*.py` — class-based system with MetricTracker, F1ScoreMetric, callback integration
- Both implement accuracy. The `src/train/` version also duplicates accuracy logic at the module level (functions `accuracy()` and `f1_score()` at lines 219–261 mirror class methods).
- **Impact:** Code duplication, inconsistent API surface, maintenance burden.
- **Fix:** Consolidate into a single metrics module.

### H-3: Test suite passes but application is broken
- **Files:** `tests/` (all)
- **Problem:** Existing tests only cover abstract base classes (`BaseModel`, `BaseDataset`). They do not test:
  - Any concrete model (MLP, CNN, Transformer in `src/models/`)
  - The working trainer (`src/train/trainer.py`)
  - The `src/train/` metrics system
  - Dataset implementations (image_datasets.py, text_datasets.py)
- Tests pass because they mock/abstract away the broken parts.
- **Impact:** False confidence — CI green but production broken.
- **Fix:** Add integration tests for the actual training pipeline and concrete model classes.

### H-4: 7 unused dependencies in requirements.txt
- **Files:** `requirements.txt` (lines 21–34)
- **Unused packages:** mlflow, optuna, pytorch-lightning, scikit-image, langchain, langchain-community, langchain-openai
- None are imported anywhere in `src/` or `tests/`.
- **Impact:** Bloated dependency tree, longer install times, increased attack surface, unnecessary transitive dependencies.
- **Fix:** Remove unused packages. Keep only what's actually imported.

### H-5: Makefile `install` target is broken
- **Files:** `Makefile` (line 15)
- **Problem:** Runs `pip install -e .` but there is no `setup.py`, `setup.cfg`, or `pyproject.toml` at the repo root. This always fails.
- **Impact:** `make install` cannot work. New developers hit a wall.
- **Fix:** Either add `pyproject.toml` with proper package metadata, or change to `pip install -r requirements.txt`.

### H-6: argocddemo — no Dockerfile, pip install on every cold start
- **Files:** `argocddemo/k8s/backend-deployment.yaml` (lines 27–29)
- **Problem:** The backend container runs `pip install --quiet fastapi uvicorn && exec uvicorn main:app ...` on every pod start. No Dockerfile exists. Every restart (reschedule, OOMKill, node drain) re-installs packages from scratch.
- **Risk:** If pip install takes longer than ~120s (liveness probe window), the pod enters CrashLoopBackOff.
- **Fix:** Build a proper Dockerfile with FastAPI + uvicorn pre-installed. Use multi-stage build for smaller image.

### H-7: argocddemo — no securityContext on any container
- **Files:** `argocddemo/k8s/backend-deployment.yaml`, `argocddemo/k8s/frontend-deployment.yaml`
- **Problem:** Neither deployment defines security context. Containers run as root by default. No `runAsNonRoot`, no `readOnlyRootFilesystem`, no capability drops.
- **Impact:** Container breakout gives full root access to the node. Fails basic PodSecurityStandards (baseline).
- **Fix:** Add `securityContext` with `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`.

### H-8: argocddemo — stale duplicate spec file
- **Files:** `argocddemo-spec.yaml` (root, 111 lines) vs `argocddemo/argocddemo-spec.yaml` (100 lines)
- **Problem:** CLAUDE.md says the root spec is the single source of truth. A second copy inside `argocddemo/` is stale — missing Hot-Reload Endpoint feature and verification section.
- **Impact:** Future edits may only touch one copy, creating drift. Developer confusion about which is authoritative.
- **Fix:** Delete the inner copy. Keep only the root spec as documented in CLAUDE.md.

---

## MEDIUM — Reliability & Best Practices

### M-1: argocddemo — frontend health probes depend on backend
- **Files:** `argocddemo/k8s/frontend-deployment.yaml` (lines 37–49), `argocddemo/k8s/configmap.yaml` (lines 34–38)
- **Problem:** Nginx proxies `/health` to the backend service. Frontend liveness/readiness probes hit `/health`. If the backend goes down, Kubernetes kills frontend pods too — cascading failure.
- **Impact:** Backend outage brings down the entire application including the frontend that could still serve static content.
- **Fix:** Serve a lightweight `/health` endpoint directly from nginx (return 200) or use a separate probe path that doesn't require the backend.

### M-2: argocddemo — insufficient startup grace period
- **Files:** `argocddemo/k8s/backend-deployment.yaml` (lines 36–48)
- **Problem:** Liveness probe allows 45s initial delay + 5 × 15s = 120s total. Cold pip install of FastAPI + uvicorn on a slow network can exceed this.
- **Impact:** Pods killed during startup, CrashLoopBackOff.
- **Fix:** Increase `initialDelaySeconds` to 90 and `failureThreshold` to 8 (giving ~210s), or better yet, use a Dockerfile (see H-6).

### M-3: argocddemo — floating image tags
- **Files:** `backend-deployment.yaml` (line 23), `frontend-deployment.yaml` (line 25)
- **Problem:** `python:3.12-slim` and `nginx:alpine` are mutable tags. A registry update silently changes the image digest on next deployment.
- **Impact:** Non-reproducible deployments. "Works today, breaks tomorrow."
- **Fix:** Pin to specific digests or versioned tags (`python:3.12.8-slim`, `nginx:1.27.0-alpine`). Update spec accordingly.

### M-4: argocddemo — no TLS anywhere
- **Files:** All argocddemo k8s manifests
- **Problem:** Ingress has no TLS section, LoadBalancer exposes HTTP only, nginx listens on port 80, backend uvicorn is HTTP-only.
- **Impact:** Zero encryption if exposed beyond the local network. Credentials and data in transit are plaintext.
- **Fix:** Add TLS to ingress with cert-manager or manual secret. At minimum, document this as a known limitation for the demo environment.

### M-5: CI never runs on development branch
- **Files:** `.github/workflows/python-package.yml` (lines 8–10)
- **Problem:** Workflow triggers only on pushes/PRs to `main`. Per CLAUDE.md, all feature work merges into `development` first. PRs from feature branches get zero CI coverage.
- **Impact:** Broken code reaches `development` undetected. CI only catches issues at the final PR to main.
- **Fix:** Add `development` to the branches list: `branches: [main, development]`.

### M-6: CI uses deprecated action version + outdated Python matrix
- **Files:** `.github/workflows/python-package.yml` (lines 19, 24)
- **Problem:** `actions/setup-python@v3` is deprecated. Python matrix `[3.9, 3.10, 3.11]` — 3.9 reached EOL in Oct 2025. Python 3.12 (used by argocddemo) is not tested.
- **Impact:** CI runs on unsupported software, missing coverage for the version actually in production.
- **Fix:** Update to `setup-python@v5`. Change matrix to `[3.11, 3.12, 3.13]`.

### M-7: argocddemo — ingress resource is dead code
- **Files:** `argocddemo/k8s/ingress.yaml`
- **Problem:** Defines host-based routing for `argocddemo.local` but no DNS record exists. No `ingressClassName` set. The spec doesn't document it. All access goes through the LoadBalancer IP (192.168.51.206).
- **Impact:** Confusion without value. Deploys resources that serve no traffic.
- **Fix:** Either configure DNS for `argocddemo.local` or remove the ingress manifest.

### M-8: ASSESSMENT.md contains false positive (BLOCKER-1)
- **Files:** `argocddemo/ASSESSMENT.md` (lines 18–42)
- **Problem:** Claims `subPath: main.py` with `mountPath: /app/main.py` "overwrites entire `/app/` directory". This is incorrect — Kubernetes `subPath` mounts only that single file path. The actual manifest is correct.
- **Impact:** Misleading future investigators. Wastes time chasing a non-issue.
- **Fix:** Update ASSESSMENT.md to remove BLOCKER-1 or mark it as resolved/false positive.

### M-9: README.md documentation is wrong
- **Files:** `README.md` (lines 15, 27–28)
- **Problem:** Quick start says `python train.py` (file doesn't exist). Directory tree shows `tests/integration/` which doesn't exist. Missing `src/train/`, `src/agents/`, `argocddemo/`.
- **Impact:** New developers follow broken instructions. Documentation misrepresents the codebase.
- **Fix:** Update README to match actual structure and working commands.

### M-10: CLAUDE.md project structure is incomplete
- **Files:** `CLAUDE.md` (lines 11–26)
- **Problem:** Documents a minimal tree that omits `src/train/`, `src/agents/`, `.github/workflows/`, `bin/`. References non-existent `conftest.py` at tests root (it exists at `tests/bdd/conftest.py`). Claims MLflow integration but no code imports MLflow.
- **Impact:** Developer onboarding guidance is inaccurate. Skills and tools reference files that don't exist.
- **Fix:** Update CLAUDE.md to reflect actual structure. Remove references to non-existent features or implement them.

### M-11: requirements.txt — lower-bound pinning only, no upper bounds
- **Files:** `requirements.txt` (all lines)
- **Problem:** Every dependency uses `>=X.Y.Z` with no ceiling. Future `pip install` pulls latest major versions which may have breaking API changes.
- **Impact:** "Works on my machine" when dependencies silently upgrade with incompatible changes.
- **Fix:** Use compatible releases (`~=2.0.0`) for stability, or maintain a locked requirements file (`requirements.lock` or `pip freeze`).

---

## LOW — Hygiene & Polish

### L-1: argocddemo — no PodDisruptionBudget
- **Files:** Missing from `argocddemo/k8s/`
- **Problem:** Both deployments have `replicas: 2` but no PDB. Node drains can terminate both pods simultaneously.
- **Fix:** Add PDB with `minAvailable: 1` per deployment.

### L-2: argocddemo — no anti-affinity rules
- **Files:** `backend-deployment.yaml`, `frontend-deployment.yaml`
- **Problem:** On multi-node clusters, both replicas could land on the same node.
- **Fix:** Add `preferredDuringSchedulingIgnoredDuringExecution` anti-affinity for pod spread.

### L-3: argocddemo — unused ConfigMap (`backend-config`)
- **Files:** `argocddemo/k8s/configmap.yaml` (lines 1–7)
- **Problem:** First ConfigMap defines `VITE_API_URL` but no Deployment references it. Leftover from a prior frontend design.
- **Fix:** Remove the unused ConfigMap.

### L-4: argocddemo — missing proxy headers on `/reload` location
- **Files:** `argocddemo/k8s/configmap.yaml` (lines 40–43)
- **Problem:** The `/reload` nginx location only sets `Host` header, missing `X-Real-IP` and `X-Forwarded-For` that the other locations set.
- **Fix:** Add consistent proxy headers.

### L-5: argocddemo — ArgoCD Application uses default project
- **Files:** `argocddemo/k8s/application.yaml` (line 7)
- **Problem:** `project: default` has no resource whitelists, no sync windows. Acceptable for demo but worth noting.
- **Fix:** Create a dedicated ArgoCD project with scoped permissions if the app grows beyond demo status.

### L-6: argocddemo — emoji in YAML ConfigMap
- **Files:** `argocddemo/k8s/configmap.yaml` (line ~325)
- **Problem:** Rocket emoji (`🚀`) in inline HTML adds multi-byte UTF-8 to a YAML value. Most tools handle it, but some terminal parsers or ArgoCD views may render incorrectly.
- **Fix:** Replace with text or an ASCII art equivalent. Minor/cosmetic.

### L-7: argocddemo — no namespace-level ResourceQuota or NetworkPolicy
- **Files:** `argocddemo/k8s/namespace.yaml`
- **Problem:** The namespace has no ResourceQuota, LimitRange, or NetworkPolicy. Pods can request unlimited resources and communicate freely.
- **Fix:** Add basic ResourceQuota and a default-deny NetworkPolicy if the cluster supports it.

### L-8: .gitignore has duplicate entries
- **Files:** `.gitignore` (lines 2/72, 28/68)
- **Problem:** `__pycache__/` listed twice. `.venv/` listed twice.
- **Fix:** Deduplicate.

### L-9: Orphaned root-level files
- **Files:** `doom-game.html`, `instruction.md`, `manual.md`, `output.txt`
- **Problem:** These files have no clear relation to the project's stated purpose (ML training + argocddemo). They add noise to the repo.
- **Fix:** Move to an archive directory, add documentation, or delete if no longer relevant.

### L-10: Makefile `clean` target uses POSIX `find` on Windows
- **Files:** `Makefile` (lines 27–30)
- **Problem:** Uses Linux `find . -type d -name ...` syntax. On Windows without Git Bash, this fails silently in PowerShell.
- **Fix:** Use a cross-platform approach or document that Makefile requires POSIX shell.

### L-11: argocddemo — SESSION-STATE.md reflects stale findings
- **Files:** `argocddemo/SESSION-STATE.md`
- **Problem:** Documents state from 2026-06-29 including BLOCKER-1 which is a false positive. Should not be used as current source of truth.
- **Fix:** Archive or update with current status.

### L-12: k8s-troubleshoot skill — add auto-activation triggers (permission-blocked)
- **Files:** `.claude/skills/k8s-troubleshoot/SKILL.md`
- **Problem:** Skill requires explicit `/k8s` invocation. No keyword-based auto-activation for phrases like "crash loop", "check the logs", "is it up". Edit was blocked by permission system on 2026-07-01.
- **Fix:** Add Auto-Activation Triggers section to SKILL.md mapping trigger phrases → subcommands. Requires manual edit or `--no-permission` flag next time.

### L-13: k8s-troubleshoot skill — assess autonomy completeness
- **Files:** `.claude/skills/k8s-troubleshoot/SKILL.md`, `bin/k8s-troubleshoot`
- **Problem:** Skill needs audit: does the bash script support all operations needed for autonomous Kubernetes troubleshooting? Missing capabilities like `get pods`, `get services`, `delete pod`, `apply manifest`, `port-forward`, `get events`, `get nodes` would block autonomous diagnosis.
- **Fix:** Audit script capabilities vs skill documentation, add missing subcommands to `bin/k8s-troubleshoot`.

---

## Summary

| Severity | Count | Theme |
|----------|-------|-------|
| CRITICAL | 4 | Security leak, broken training pipeline |
| HIGH     | 8 | Duplicate code paths, unused deps, missing Dockerfile, no security context |
| MEDIUM   | 11 | CI gaps, cascading failures, outdated docs, stale assessments |
| LOW      | 11 | Hygiene, PDBs, anti-affinity, orphaned files |

**Total: 34 items**

---

## Recommended Priority Order

Address these in order for maximum impact:

1. **C-1** — Rotate the API key (do this outside git)
2. **C-2 + C-3 + C-4** — Fix the broken training pipeline (they're related)
3. **H-5** — Fix Makefile so `make install` works
4. **H-4** — Remove unused dependencies
5. **M-9 + M-10** — Update README and CLAUDE.md to match reality
6. **H-1 + H-2** — Decide: consolidate or document the dual training systems
7. **M-5 + M-6** — Fix CI so it actually runs on development
8. **H-3** — Add real tests for the working code paths
9. **C-2 cleanup** — Purge API key from git history (can be done after rotation)
10. **argocddemo issues** (H-6 through L-11) — Tackle when the cluster is active
