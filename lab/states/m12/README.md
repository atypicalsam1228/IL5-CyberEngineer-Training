# M12 start state: Backup and Recovery

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-demo-app.sh, 20-pvc-demo-data.yaml and 30-mount-demo-data.sh (claim demo-data mounted at /data, write tested), 40-oadp-operator.sh (installs redhat-oadp-operator, no DataProtectionApplication), 50-backup-credentials.sh (IAM user velero-<LAB_ID> and secret cloud-credentials), 60-preflight-bucket.sh. reset.d removes dpa-demo, the schedule, backup, restore and demo-restored.
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
