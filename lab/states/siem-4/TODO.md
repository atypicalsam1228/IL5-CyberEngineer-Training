# TODO: start state for SIEM-4 (Respond to an Incident)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: demo-app in demo, role binding demo-extra-admin, and the Grafana contact point and privilege-change rule so the alert can fire.
- [live] 1: The alert actually reaches siem-alerts after the binding is created (rule evaluation interval, audit field names). It fires once, when the binding is first created.
- [live] 2: NetworkPolicy enforced (OVN-Kubernetes default).
- [lab-build] 3: Mattermost reachable at mattermost.chat.svc.cluster.local:8065 and the learner has an account that can create channels.
+ [done] 4: Service account auditor in siem bound to audit-log-reader.

Open items from review (live test or decision):
- Live check: Loki query, ping endpoint, quarantine codes 200 and 000 (review SIEM-4).
