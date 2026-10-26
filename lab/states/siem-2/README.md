# SIEM-2 start state: Store and Protect Audit Logs

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-forwarder.sh (SIEM-1 end state if missing, without delivery tuning), 20-loki-config.yaml (the starting loki-config: schema v13 from 2024-04-01, filesystem storage, retention off, no deletion setting), 30-loki-env-and-restart.sh (sets LOG_BUCKET, KMS_KEY_ARN, AWS_REGION on deployment loki and rolls it when the config changed), 40-audit-log-reader-role.sh (role created only if missing), 50-preflight-storage-and-grafana.sh. reset.d removes the auditor and ordinary-user accounts, the delivery tuning and the siem-storage Grafana folder.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: SIEM-1 Collect Audit Logs

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
