# TODO: start state for M06 (Privileged Access and Session Audit)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Checks session-manager-plugin is on the PATH.
- [lab-build] 1: Session Manager plugin baked into the tools image.
+ [done] 2: Checks the three SSM interface endpoints exist in VPC_ID (created by terraform/endpoints.tf when enable_ssm_endpoints is true).
- [live] 3: AWS credentials allow creating EC2, IAM, CloudWatch Logs and Systems Manager resources and reading the public AMI parameter (only the real apply shows it).
+ [done] 4: Checks the KMS key policy lets CloudWatch Logs use the key.
+ [done] 5: Checks SSM-SessionManagerRunShell does not exist yet.
- [live] 6: Terraform can download the AWS provider from the internet.
+ [done] 7: Checks audit logs are in Loki and a push is accepted; recreates the SIEM-1 forwarder if missing.

Open items from review (live test or decision):
- See the review log for the unresolved list.
