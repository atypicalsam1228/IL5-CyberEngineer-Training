# M05 start state: Identity and Multi-Factor Sign-In

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-preflight-keycloak.sh (read-only: Keycloak answers over HTTPS with the cluster ingress CA, admin token issued, secret card-ca present, warns if realm il5 exists) and 20-preflight-oauth.sh (read-only: no other identity providers). reset.d removes the il5 realm, the OpenShift Keycloak provider, its secret and config map.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
