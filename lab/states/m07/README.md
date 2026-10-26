# M07 start state: Hardening and Policy as Code

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-demo-app.sh (demo-app with a fixed tag and runAsNonRoot, checked), 20-compliance-operator.sh (installs compliance-operator and waits for VALID ProfileBundles), 30-preflight-kyverno.sh (read-only). reset.d removes the three Kyverno ClusterPolicies.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
