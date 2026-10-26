# SIEM-1 start state: Collect Audit Logs

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-logging-operator.sh (installs cluster-logging in openshift-logging and waits for the three collect-* cluster roles), 20-preflight-loki.sh (Loki answers ready). It creates no collector, secret or forwarder: steps 2 and 3 build those. reset.d removes them.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
