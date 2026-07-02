# ArgoCD Demo — Assessment Report

**Date:** 2026-06-29  
**Author:** Claude Code (Claude Sonnet 4)  
**Triggered by:** User request to assess argocddemo app state against spec-driven development workflow  
**Cluster status:** UNREACHABLE — no kubeconfig pointing to any Kubernetes API server

---

## Executive Summary

The argocddemo application's manifests and source code are committed to the repository (`argocddemo/` directory) and appear structurally correct for the spec. However, **the local Kubernetes cluster is not reachable**, so no live assessment of running pods, services, or endpoints was possible. Additionally, a critical bug exists in the backend deployment manifest that will cause runtime failure.

---

## Blockers (Must Fix Before Deployment Works)

### BLOCKER-1: Backend ConfigMap Volume Mount Path BUG — WILL FAIL AT RUNTIME

**File:** `argocddemo/k8s/configmap.yaml` + `argocddemo/k8s/backend-deployment.yaml`  
**Severity:** CRITICAL — deployment will fail to start

**Problem:** The backend deployment mounts the configMap file `main.py` at path `/app/main.py` (a file path, not a directory):

```yaml
volumeMounts:
  - name: app-code
    mountPath: /app/main.py       # ← overwrites entire /app/ directory
    subPath: main.py
```

This mounts the configMap entry as the **entire** `/app/` mount point, which replaces the directory. The uvicorn command expects `workingDir: /app` and imports from that context — this mount path will prevent Python from finding packages or the app itself.

**Correct pattern:** Mount at the parent directory:
```yaml
volumeMounts:
  - name: app-code
    mountPath: /app                 # mounts configMap contents as /app/main.py inside
```

The container image `python:3.12-slim` is an OS-only base — uvicorn/fastapi won't be available until pip install runs. This is addressed by the command, but the volume mount must not clobber `/app/`.

---

### BLOCKER-2: No Kubernetes Cluster Configured

**Symptom:** `kubectl get pods -n argocddemo` returns connection refused to localhost:8080  
**Impact:** Cannot deploy, verify, or troubleshoot the application  

**Root cause:** kubeconfig does not point to a valid cluster API server. This is a local environment setup issue, not a code problem.

**Required fix (user action needed):**
1. Ensure `kubectl` can reach the cluster (e.g., via Docker Desktop Kubernetes, kind, minikube, or k3s)
2. Verify with: `kubectl cluster-info`
3. Verify namespace visibility: `kubectl get namespaces | grep argocddemo`

---

### BLOCKER-3: Frontend Deployment Uses Unpinned Nginx Image

**File:** `argocddemo/k8s/frontend-deployment.yaml` line 25  
**Severity:** HIGH — will break unexpectedly when nginx:alpine tag updates

```yaml
image: docker.io/nginx:alpine     # no digest or patch version pinned
```

**Recommendation:** Pin to a specific digest for reproducible deployments:
```yaml
image: docker.io/nginx@sha256:<digest>
```
or at minimum a minor tag like `nginx:1.27-alpine`.

---

## Spec Compliance Analysis

Each spec feature vs manifest implementation:

### Feature 1: Landing Page (GET / → 200, body_contains ...)

| Checkpoint | Status | Notes |
|---|---|---|
| index.html in nginx-static configMap | PASS | Contains DOCTYPE, ARGOCD DEMO, Mission Control |
| rocket-wrap class | PASS | SVG present with Saturn V styling |
| smoke-puff elements | PASS | 4 puffs defined |
| @keyframes float | PASS | Included in CSS |
| @keyframes flamePulse | PASS | Included in CSS |
| ALL SYSTEMS NOMINAL | PASS | In console div |
| Frontend deployment (replicas:2) | MATCHES spec replicas=2 | |
| Frontend service (LoadBalancer:80) | MATCHES spec | LoadBalancer IP = 192.168.51.206 per cluster config |

**Verdict:** PASS — All spec assertions covered. **But frontend nginx has a health probe issue (see OBSERVATION-1).**

---

### Feature 2: Health Check Proxy (GET /health → {"status":"healthy","version":"0.1.0"})

| Checkpoint | Status | Notes |
|---|---|---|
| Backend /health endpoint defined | PASS | Returns correct JSON |
| Nginx proxy /health location | PASS | Proxies to backend:8000/health |
| Frontend readiness probe → /health | ISSUE | Frontend probes `/health` on its own static HTML (returns 404) |

**Verdict:** PARTIAL PASS — Backend endpoint correct, nginx proxy chain correct, but frontend readiness probe will fail in production.

---

### Feature 3: Items API Proxy (GET /api/items → array of 5 widgets)

| Checkpoint | Status | Notes |
|---|---|---|
| _ITEMS list in main.py (5 items) | PASS | IDs 1-5, Widget A through E |
| Backend /api/items endpoint | PASS | Returns _ITEMS |
| Nginx proxy /api/ location | PASS | Proxies to backend:8000/api/ |

**Verdict:** PASS — All spec assertions covered.

---

### Feature 4: Hot-Reload Endpoint (POST /reload → {"ok": true})

| Checkpoint | Status | Notes |
|---|---|---|
| Backend POST /reload endpoint | PASS | exec-based reload from ConfigMap mount |
| Nginx proxy /reload location | PASS | Proxies to backend:8000/reload |
| ConfigMap main.py content matches mounted path | ISSUE | Same BUG as BLOCKER-1 |

**Verdict:** PARTIAL PASS — Code correct in logic but **will fail due to volume mount bug (BLOCKER-1).**

---

## Infrastructure Compliance

### Spec vs Manifest Comparison

| Spec Requirement | Manifest | Match? |
|---|---|---|
| backend replicas: 2 | backend-deployment.yaml replicas: 2 | PASS |
| backend image: python:3.12-slim | backend deployment image: python:3.12-slim | PASS |
| backend port: 8000 | containerPort 8000, service port 8000 | PASS |
| frontend replicas: 2 | frontend-deployment.yaml replicas: 2 | PASS |
| frontend image: nginx:alpine | frontend deployment image: nginx:alpine | PARTIAL (unpinned) |
| frontend port: 80 | containerPort 80, service port 80 | PASS |
| backend service ClusterIP:8000 | backend-service.yaml type=ClusterIP port=8000 | PASS |
| frontend service LoadBalancer:80 | frontend-service.yaml type=LoadBalancer port=80 | PASS |

---

## Observations (Non-Blocking but Notable)

### OBSERVATION-1: Frontend Readiness/Liveness Probes Will Fail

**File:** `argocddemo/k8s/frontend-deployment.yaml` lines 37-49

The frontend deployment has readiness and liveness probes targeting `/health` on port 80. Since nginx serves static HTML (no backend proxy for `/health`), the default 404 response will cause pods to be marked Unhealthy.

**Fix options:**
1. Change probe path to `/` (the index.html returns 200) — simplest fix
2. Add a `/health` location in nginx that returns 200 manually: `return 200 '{"status":"ok"}'; add_header Content-Type text/json;`

---

### OBSERVATION-2: Backend Startup is Fragile

**File:** `argocddemo/k8s/backend-deployment.yaml` line 27

```yaml
command: ["/bin/sh", "-c"]
args: ["pip install --quiet fastapi==0.115.6 uvicorn==0.34.0 && exec uvicorn main:app ..."]
```

- Each pod restart triggers a full `pip install` from scratch (no cached layer)
- InitialDelaySeconds=30 for readiness and 45 for liveness may be insufficient if pip install takes >45s on slow networks
- No Dockerfile — this is an anti-pattern for production

---

### OBSERVATION-3: Ingress Resource May Be Unnecessary

**File:** `argocddemo/k8s/ingress.yaml`

The ingress configures host-based routing for `argocddemo.local`, which is not part of the spec. The spec uses only the LoadBalancer IP (192.168.51.206). This Ingress is dead code unless someone manually adds DNS records. If it stays, it needs an `ingressClassName` annotation.

---

### OBSERVATION-4: ConfigMap Name Mismatch for Backend Config

**File:** `argocddemo/k8s/configmap.yaml` line 4

The configMap is named `backend-config` but the backend-deployment references `backend-app-config`. There are two separate configMaps being created:
- `backend-config` — has `VITE_API_URL` (unused by anything currently)
- `backend-app-config` — has `main.py` (actually mounted)

The `VITE_API_URL` reference seems to be leftover from a previous Vite-based frontend that no longer exists. It's harmless but confusing.

---

## Missing Artifacts Per Spec

The spec defines these infrastructure components — checking what's missing:

| Component | Manifest Present? |
|---|---|
| argocddemo namespace | YES (namespace.yaml) |
| backend Deployment (2 replicas) | YES |
| backend Service (ClusterIP) | YES |
| frontend Deployment (2 replicas) | YES |
| frontend Service (LoadBalancer:80) | YES |
| nginx config ConfigMap | YES |
| nginx static content ConfigMap | YES |
| backend app code ConfigMap | YES |
| ArgoCD Application resource | YES |
| **Ingress** | YES (unnecessary per spec) |

No missing infrastructure artifacts. All required K8s resources have manifests.

---

## Required Actions Summary

### Must Fix Before Deploy (Blocking)
1. **[BLOCKER-1]** Fix backend ConfigMap volume mount path from `/app/main.py` to `/app`
2. **[BLOCKER-2]** Configure kubeconfig to reach cluster (user action)
3. **[BLOCKER-3]** Pin nginx image tag or digest

### Should Fix Before Production
4. **[OBSERVATION-1]** Fix frontend health probe path from `/health` to `/`
5. **[OBSERVATION-2]** Build proper Dockerfile for backend instead of pip install at startup
6. **[OBSERVATION-3]** Remove or document the ingress.yaml (dead code)
7. **[OBSERVATION-4]** Clean up unused `backend-config` configMap

---

## Verification Steps (Once Cluster Is Reachable)

Run this checklist after fixing blockers and deploying:

```bash
# 1. Check pods
kubectl get pods -n argocddemo

# 2. Check services
kubectl get svc -n argocddemo

# 3. Verify endpoints
curl http://192.168.51.206/           # should return landing page HTML
curl http://192.168.51.206/health     # should return {"status":"healthy","version":"0.1.0"}
curl http://192.168.51.206/api/items  # should return array of 5 widgets
curl -X POST http://192.168.51.206/reload  # should return {"ok":true}

# 4. If anything fails, debug:
kubectl describe pods -n argocddemo    # check events (OOMKilled, CrashLoopBackOff, etc.)
kubectl logs <pod> -n argocddemo       # check container logs
```
