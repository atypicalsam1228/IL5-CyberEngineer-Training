# M02 start state: Lab Build with Terraform

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-preflight.sh: read-only checks of AWS identity, exactly one public Route 53 zone, the pull secret, ssh-keygen and GNU date. No cluster steps (the cluster does not exist yet at M02).
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
