# TODO: start state for M09 (Secure Release Pipeline)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Gitea repo demo-app with app, tests (unittest, full coverage of the testable code on both branches) and Dockerfile on main and critical-finding.
- [live] 1: Confirm with trivy that main has no HIGH or CRITICAL and critical-finding has at least one, and that coverage is at least 80 percent when the tools image runs it.
- [lab-build] 2: Tool images tools/python-test:lab, tools/trivy:lab, tools/cosign:lab in REGISTRY_HOST and a reachable Trivy database (needs an image build and push; outside oc/curl/jq).
+ [done] 3: registry-pull in kyverno and the registry credential linked to service account pipeline in build.
- [live] 3: ASSUMPTION: REGISTRY_HOST accepts GITEA_USER and GITEA_TOKEN; repository demo/demo-app accepts pushes from the pipeline account.
- [lab-build] 4: Cosign 3.x in the tools image and lab shell, Kyverno 1.19 or earlier, registry certificate trust in Kyverno, lab shell logged in to REGISTRY_HOST (Helm and cosign are outside the allowed tools for state scripts).
- [lab-build] 5: Gitea and registry certificate trust in pipeline pods and the lab shell; git credential helper in the tools image.
+ [done] 6: Deployment demo-app (container demo-app) exists in demo; OpenShift Pipelines and its tasks installed; Kyverno presence checked.
- [lab-build] 6: Start demo-app from an image signed by the lab build (needs registry access and cosign sign).

Open items from review (live test or decision):
- Decision: pin Kyverno <= 1.19 or convert Step 3 to ImageValidatingPolicy (review M09).
