# TODO: start state for M08 (Vulnerability Management)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

- [lab-build] 1: Trivy Operator in security-tools scoped to vuln-lab, with a reachable vulnerability database or mirror (Helm install; exact deployment and variable names need the real chart).
- [live] 2: Lab shell can pull docker.io/library/nginx:1.16 and cgr.dev/chainguard/static:latest, or a mirror is set up and the module text updated.

Open items from review (live test or decision):
- See the review log for the unresolved list.
