# TODO: start state for SIEM-3 (Detect and Alert)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Checks Grafana has data sources Loki and Prometheus.
- [live] 1: Prometheus data source returns node_timex_sync_status.
- [lab-build] 2: Mattermost channel siem-alerts with an incoming webhook, MM_WEBHOOK_URL pointing to it.
- [lab-build] 3: Keycloak writes login events to its container log (Keycloak event logging setup).
- [lab-build] 4: The Grafana Loki data source authenticates with an identity bound to audit-log-reader.
+ [done] 5: Service account auditor in siem bound to audit-log-reader; siem-forwarder provided.
+ [done] 6: Checks KEYCLOAK_URL and the Loki CA variables are set.

Open items from review (live test or decision):
- Live check: audit field names in Loki, Keycloak LOGIN_ERROR text, daemonset name equals CLF name (review SIEM-3).
