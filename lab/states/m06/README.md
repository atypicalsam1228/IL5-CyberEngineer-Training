# M06 start state: Privileged Access and Session Audit

Applied by `lab start` / `lab reset` in file-name order. `.sh` files run with bash and must be idempotent;
.yaml/.json files are applied with `oc apply -f`. Files in `reset.d/` run first on `lab reset` only.

Implemented: 10-demo-app.sh (namespace demo, demo-app), 20-siem-forwarder.sh (SIEM-1 end state if missing), 30-preflight-aws.sh (Session Manager plugin, ssm/ssmmessages/ec2messages endpoints in VPC_ID, KMS policy for CloudWatch Logs, no SSM-SessionManagerRunShell yet), 40-preflight-loki.sh (audit logs present, push accepted). reset.d removes the RBAC M06 creates and the SSM documents (refuses while the jump host exists).
Still needed (live cluster or lab build): see TODO.md. `lab start` prints it while TODO.md exists.

Prerequisites: Module 0 (terminal and git basics); Module 2 (lab running); SIEM-1 (audit logs reaching Loki)

Scripts here have not been run on a live cluster or account. Shared helpers: ../_common/lib.sh (sourced by the scripts) and ../_common/demo-app.yaml.
