# M10 start state: GitOps and Change Control

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-demo-app.sh, 20-gitops-and-file-integrity.sh (OpenShift GitOps and File Integrity Operator), 30-gitea-demo-config-repo.sh (repository demo-config with deployment.yaml built from the running demo-app, service.yaml, user lab-reviewer with write access), 40-demo-not-managed.sh. reset.d removes the Argo CD application, project, repository secret, RBAC patch, FileIntegrity and the Gitea branch protection.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running); M09 Secure Release Pipeline (signed demo-app image)

Note: Kyverno enforce policies from M07 persist in the demo namespace unless you run `lab reset m07`.

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
