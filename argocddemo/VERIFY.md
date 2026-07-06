# ArgoCD Demo — Verification Checklist

Use this checklist for every change to the argocddemo application.
Tick each box only after confirming it against the live cluster at **192.168.51.206**.

---

## Pre-Commit

- [ ] Read `argocddemo-spec.yaml` — understand what currently exists
- [ ] Update `argocddemo-spec.yaml` to reflect the new desired state
- [ ] Implement K8s manifests / source to match the updated spec
- [ ] If static content changed, bump `checksum/nginx-static` in `frontend-deployment.yaml`
- [ ] If nginx config changed, bump `checksum/nginx-config` in `frontend-deployment.yaml`
- [ ] Commit message uses conventional prefix (`feat:`, `fix:`, `docs:`, etc.)

## Post-Push (Run Before Marking Done)

- [ ] ArgoCD synced new manifests (check pod restart / rollout status)
- [ ] `kubectl get pods -n argocddemo` — all replicas Running and Ready per spec
- [ ] `kubectl get hpa -n argocddemo` — HPA targeting correct deployments
- [ ] `kubectl get pdb -n argocddemo` — PDBs with minAvailable: 1
- [ ] `kubectl get networkpolicy -n argocddemo` — 4 policies present
- [ ] `kubectl describe namespace argocddemo` — pod-security labels = restricted
- [ ] `kubectl describe resourcequota -n argocddemo` — quota within bounds
- [ ] Curl each affected endpoint at `http://192.168.51.206` — response matches spec "then" clauses
- [ ] If probes changed, `kubectl describe pods <pod> -n argocddemo` — events confirm correct path/port

## Quick Health Check

```powershell
curl http://192.168.51.206/            # landing page (200, contains "ARGOCD DEMO")
curl http://192.168.51.206/health      # {"status":"healthy","version":"0.1.0"}
curl http://192.168.51.206/api/items   # 5 widgets array
curl -X POST http://192.168.51.206/reload  # {"ok":true}
```

## If Anything Fails

**Do not push.** Diagnose the mismatch, fix it, recommit, and re-verify.
