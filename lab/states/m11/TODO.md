# TODO: start state for M11 (Malware and Runtime Detection)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

- [lab-build] 1: ClamAV deployment clamav with clamd on 3310, freshclam, and PVC uploads mounted at /scan (image pins and manifests not decided).
- [lab-build] 2: Falco daemonset with modern_ebpf, json_output and container metadata (Helm install; privileges on the OpenShift node).
+ [done] 3: Config map falco-custom-rules exists.
- [live] 3: Mounted at /etc/falco/rules.d in the Falco daemonset (set by the Falco install).
+ [done] 4: demo-app image has a working sh (checked with oc exec).

Open items from review (live test or decision):
- See the review log for the unresolved list.
