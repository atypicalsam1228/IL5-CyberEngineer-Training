# SIEM-3 start state: Detect and Alert

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-forwarder.sh (SIEM-2 end state for the forwarder, with delivery tuning), 15-audit-log-reader-role.sh, 20-auditor.sh (service account auditor bound to audit-log-reader), 30-preflight-grafana-and-mattermost.sh (read-only).
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: SIEM-1 Collect Audit Logs; SIEM-2 Store and Protect Audit Logs

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
