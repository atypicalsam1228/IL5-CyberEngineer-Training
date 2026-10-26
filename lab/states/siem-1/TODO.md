# TODO: start state for SIEM-1 (Collect Audit Logs)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

The module lists no lab needs. Live checks are under the review items below.


Open items from review (live test or decision):
- Live checks (review SIEM-1): ClusterRoles collect-application-logs, collect-audit-logs, collect-infrastructure-logs exist after the Logging Operator; log_type label in Loki; basic auth block for Loki.
