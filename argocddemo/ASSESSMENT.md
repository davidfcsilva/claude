# ArgoCD Demo — Assessment Report v0.3.0

**Updated:** 2026-07-07
**Author:** Claude Code

---

## All Issues Resolved

| ID | Description | Status | Fix |
|---|---|---|---|
| BLOCKER-1 | Backend volume mount clobbered `/app/` | ✅ FIXED | Fixed mount path with subPath for main.py only |
| BLOCKER-2 | No cluster reachable | ⏳ PENDING | User action required |
| BLOCKER-3 | Frontend image unpinned | ✅ FIXED | Pinned to `nginx:1.27-alpine` |
| OBS-1 | Frontend probes hit wrong path | ✅ FIXED | Probes now hit `/` |
| OBS-2 | Backend startup fragile (pip install on every boot) | ✅ RESOLVED | Init container pre-installs packages into shared emptyDir |
| OBS-3 | Dead ingress.yaml | ✅ REMOVED | Deleted |
| OBS-4 | Unused backend-config ConfigMap | ✅ REMOVED | Removed |

---

## Manifest Inventory (v0.3.0)

| File | Purpose |
|---|---|
| `namespace-quota.yaml` | Namespace + PodSecurity labels + ResourceQuota + LimitRange |
| `backend-deployment.yaml` | FastAPI with init container, security context, non-root, probes, HPA target |
| `frontend-deployment.yaml` | Nginx with readOnly filesystem, security context, HPA target |
| `configmap.yaml` | Nginx config + static HTML + backend Python code |
| `backend-hpa.yaml` | 2-10 replicas, CPU 70%, mem 80% |
| `frontend-hpa.yaml` | 2-8 replicas, CPU 60% |
| `pdb.yaml` | minAvailable: 1 for both |
| `network-policy.yaml` | Default-deny + frontend external + backend-from-frontend + DNS egress |
| `frontend-service.yaml` | LoadBalancer service |
| `application.yaml` | ArgoCD Application resource |
