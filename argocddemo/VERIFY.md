# ArgoCD Demo — Verification Checklist

Use this checklist for every change to the argocddemo application.
Tick each box only after confirming it against the live cluster at **192.168.51.206**.

---

## Pre-Commit

- [ ] Read `argocddemo-spec.yaml` — understand what currently exists
- [ ] Update `argocddemo-spec.yaml` to reflect the new desired state
- [ ] Implement K8s manifests / source to match the updated spec
- [ ] If static content changed, bump `checksum/nginx-static` in `frontend-deployment.yaml`
- [ ] Commit message uses conventional prefix (`feat:`, `fix:`, `docs:`, etc.)

## Post-Push (Run Before Marking Done)

- [ ] ArgoCD synced new manifests (check pod restart / rollout status)
- [ ] `kubectl get pods -n argocddemo` — all replicas Running and Ready per spec
- [ ] `kubectl get svc frontend -n argocddemo` — type, port, LoadBalancer IP match spec
- [ ] Curl each affected endpoint at `http://192.168.51.206` — response matches spec "then" clauses
- [ ] If probes changed, `kubectl describe pods <pod> -n argocddemo` — events confirm correct path/port

## If Anything Fails

**Do not push.** Diagnose the mismatch, fix it, recommit, and re-verify.
If the change intentionally modifies behaviour, update the spec first, then verify against that updated spec.
