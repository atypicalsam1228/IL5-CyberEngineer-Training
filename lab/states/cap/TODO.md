# TODO: start state for CAP (Capstone)

- Confirm the demo-app image answers HTTP on port 8080 (checks 5 and 6 and the Service use 8080).
- Confirm secret registry-pull exists in namespace kyverno and is a Docker config secret.
- Confirm Gitea user lab-reviewer exists with write access to cap-config (as for demo-config in M10) and that GITEA_TOKEN belongs to an administrator.
- Confirm the Loki read with LOKI_USER and LOKI_PASSWORD still works after SIEM-2 (check 7).
- Run 10-gitea-repo.sh and the reset script once in a live lab and fix any API differences in your Gitea release.

- 10-gitea-repo.sh now adds lab-reviewer as a write collaborator before saving the rule (Gitea drops allow-list users without repo access); lab-reviewer must exist.
- Pin or record the Gitea version; API fields were checked against Gitea main source.
