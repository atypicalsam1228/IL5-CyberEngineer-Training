# CAP start state: Capstone

Applied by `lab start cap` / `lab reset cap`. Scripts are idempotent.

Implemented:
- 10-gitea-repo.sh creates Gitea repository cap-config (README on main) and protects main (no direct push, one approval from lab-reviewer).
- reset.d/10-clean-cap.sh removes project cap-demo, the Argo CD application and repo secret, and takes cap-demo out of the Kyverno policy require-signed-images.

Not implemented: see TODO.md (live-lab items). Nothing here has run against a cluster.

Prerequisites: end state of SIEM-1, SIEM-2, M03, M06, M09, M10.
