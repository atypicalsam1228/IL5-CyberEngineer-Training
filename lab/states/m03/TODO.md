# TODO: start state for M03 (Boundary and Default-Deny)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Operator, Istio default and IstioCNI default (20-service-mesh-operator.sh, 30-istio.yaml, 40-wait-healthy-and-network.sh).
- [live] 1: Confirm the sailoperator.io/v1 field names (spec.namespace, spec.updateStrategy.type) and that no spec.version is needed on the installed operator release.
- [live] 2: Cluster can pull registry.access.redhat.com/ubi9/ubi-minimal and ubi9/python-311 (a pull test only a live cluster can run).
+ [done] 3: Checks the network type is OVNKubernetes.

Open items from review (live test or decision):
- See the review log for the unresolved list.
