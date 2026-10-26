# TODO: start state for M10 (GitOps and Change Control)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Gitea repo demo-config with deployment.yaml (replicas: 1, the image demo-app runs now) and service.yaml on main; user lab-reviewer with write access.
- [live] 1: Confirm GITEA_TOKEN is an administrator token (user creation fails otherwise) and that the generated deployment.yaml syncs cleanly.
+ [done] 2: OpenShift GitOps installed; waits for ArgoCD openshift-gitops and its repo server.
- [lab-build] 2: Argo CD repo server trusting the Gitea certificate; argocd core mode in the tools image.
+ [done] 3: File Integrity Operator in openshift-file-integrity.
- [lab-build] 4: Git credential helper, git identity and Gitea certificate trust in lab shell.
+ [done] 5: demo-app runs in demo and the Argo CD managed-by label is absent.

Open items from review (live test or decision):
- See the review log for the unresolved list.
