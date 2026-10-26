# SIEM-4 start state: Respond to an Incident

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: Creates namespace demo, Deployment demo-app (25-demo-app.sh, label app=demo-app, service account demo-app, image with curl, checked), service accounts auditor (siem) and demo-app (demo), the SIEM-3 Mattermost contact point and privilege-change rule (28-alert-rule.sh), and role binding demo-extra-admin (admin role for demo-app in demo).
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: SIEM-1 Collect Audit Logs; SIEM-2 Store and Protect Audit Logs; SIEM-3 Detect and Alert

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
