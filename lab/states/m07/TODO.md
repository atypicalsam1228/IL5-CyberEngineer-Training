# TODO: start state for M07 (Hardening and Policy as Code)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Compliance Operator in openshift-compliance, ProfileBundles VALID.
- [live] 1: ProfileBundle status field name dataStreamStatus and the default channel need a live check.
+ [done] 2: demo-app uses ubi9/ubi-minimal:9.5 and runAsNonRoot: true; the script fails if an existing demo-app does not.
- [lab-build] 3: Kyverno 1.19.2 (Helm chart 3.9.2) in namespace kyverno needs Helm, which is outside the allowed tools for state scripts.
+ [done] 3: Checks the Kyverno namespace, the ClusterPolicy CRD and a running pod.

Open items from review (live test or decision):
- Policies stay Enforce in demo after M07; run 'lab reset m07' to remove them. Later modules M04, M03, M09, M10 create pods in demo and must comply or you must reset (review M07).
