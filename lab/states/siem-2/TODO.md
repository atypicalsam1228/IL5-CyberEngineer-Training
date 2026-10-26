# TODO: start state for SIEM-2 (Store and Protect Audit Logs)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: loki-config start state, the three environment variables, restart on change.
- [lab-build] 1: Deployment loki with -config.expand-env=true and an AWS identity for the bucket and key (the script fails with a clear message if the argument is missing).
+ [done] 2: Checks the log bucket: Compliance default retention, aws:kms encryption, Glacier transition (bucket built by terraform/storage.tf).
- [live] 2: The Compliance retention period is short enough for compactor errors to clear within a session.
- [live] 3: The Loki endpoint accepts Kubernetes bearer tokens and returns 403 unless the token is bound to audit-log-reader. ClusterRole audit-log-reader is created only if missing; the rule the endpoint checks needs a live check.
+ [done] 4: Checks Grafana has data sources Loki and Prometheus.
+ [done] 5: Provides the SIEM-1 end state (siem-forwarder) and the starting loki-config.

Open items from review (live test or decision):
- loki-config must use schema v13 from 2024-04-01 or Step 3 conflicts (review SIEM-2).
- Short Object Lock period so compactor errors clear within a session (review SIEM-2).
