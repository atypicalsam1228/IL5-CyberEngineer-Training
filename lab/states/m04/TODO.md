# TODO: start state for M04 (FIPS Cryptography and Keys)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

- [lab-build] 1: IAM permissions for the KMS, EC2 and S3 calls (terraform/iam_installer.tf and the lab identity).
- [lab-build] 2: KMS key policy allowing the storage-driver and backup roles (terraform/kms.tf; tighten by role name after the cluster exists).
- [live] 3: The existing scripts (10-etcd-and-tls-off.sh, 20-key-rotation-off.sh) have not run on a live cluster; encryption off may take time to settle.
- [lab-build] 4: openssl s_client -cipher and AWS CLI v2 in the tools image.
- [live] 5: Router reachable on 443 from the lab network.

Open items from review (live test or decision):
- See the review log for the unresolved list.
