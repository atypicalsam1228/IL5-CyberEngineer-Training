# TODO: start state for M00 (Keyboard Survival and Machine Check)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

- [lab-build] 1: Published laptop minimum spec and lab install page (documentation, not a start state).
+ [done] 2: demo namespace and Deployment demo-app (20-demo-app.sh using _common/demo-app.yaml).
- [live] 2: Confirm on a live cluster that the demo-app pod reaches Running (image tag 9.5 exists in the Red Hat registry).

Open items from review (live test or decision):
- Confirm docker info --format field name ServerVersion; exact oc error text for a missing namespace on 4.22 (review M00).
