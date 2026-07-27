# ArgoCD Demo — v0.3.0

FastAPI + nginx demo app deployed via ArgoCD to Kubernetes with production-grade scalability and security features.

## Architecture

```
LoadBalancer (192.168.51.206:80)
  └── frontend Service → nginx pods [HPA: 2-8]
         ├── /        → landing page (festive tree SVG)
         ├── /health  → backend health check
         ├── /api/*   → backend API proxy
         └── /reload  → hot-reload endpoint
```

## Endpoints

| Path | Method | Response |
|---|---|---|
| `/` | GET | Landing page (200) |
| `/health` | GET | `{"status":"healthy","version":"0.1.0"}` |
| `/api/items` | GET | Array of 5 widgets |
| `/reload` | POST | `{"ok":true}` |

## Scalability Features

- **HPA**: Auto-scaling on CPU/memory (backend: 2-10, frontend: 2-8 replicas)
- **PDB**: Pod Disruption Budgets ensure minimum availability during drains
- **Anti-affinity**: Pods spread across nodes for high availability
- **RollingUpdate**: Zero-downtime deployments

## Security Features

- **NetworkPolicy**: Default-deny ingress; frontend accepts external only; backend accepts frontend only
- **Pod Security Standards**: Restricted profile enforced at namespace level
- **readOnlyRootFilesystem**: All containers run with read-only filesystems
- **Non-root**: Backend runs as UID 65534 (nobody)
- **Capabilities**: All Linux capabilities dropped from every container

## Manifest Inventory

| File | Purpose |
|---|---|
| `namespace-quota.yaml` | Namespace + PodSecurity + ResourceQuota + LimitRange |
| `backend-deployment.yaml` | FastAPI backend with init container, security context |
| `frontend-deployment.yaml` | Nginx frontend with security context |
| `configmap.yaml` | Nginx config + static HTML + backend Python code |
| `backend-hpa.yaml` | HorizontalPodAutoscaler for backend |
| `frontend-hpa.yaml` | HorizontalPodAutoscaler for frontend |
| `pdb.yaml` | PodDisruptionBudgets |
| `network-policy.yaml` | NetworkPolicies (zero-trust) |
| `frontend-service.yaml` | LoadBalancer service |
| `application.yaml` | ArgoCD Application resource |
