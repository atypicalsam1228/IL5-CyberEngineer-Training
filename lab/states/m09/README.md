# M09 start state: Secure Release Pipeline

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-pipelines-and-namespaces.sh (OpenShift Pipelines, namespace build, waits for the pipeline service account and tasks, checks Kyverno), 20-demo-app.sh, 30-registry-credentials.sh (registry-pull in kyverno, registry-credentials in build linked to pipeline), 40-gitea-demo-app-repo.sh (repository demo-app: app.py, tests, Dockerfile on main and critical-finding). reset.d removes everything M09 creates.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Note: Kyverno enforce policies from M07 persist in the demo namespace unless you run `lab reset m07`.

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
