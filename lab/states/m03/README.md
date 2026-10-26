# M03 start state: Boundary and Default-Deny

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: Installs OpenShift Service Mesh 3 (servicemeshoperator3, default channel), creates namespaces istio-system and istio-cni, Istio default (InPlace) and IstioCNI default, waits until both are Ready, and checks the OVN-Kubernetes network plugin. The module itself creates namespace boundary-lab, so nothing in demo is used.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Note: Kyverno enforce policies from M07 persist in the demo namespace unless you run `lab reset m07`.

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
