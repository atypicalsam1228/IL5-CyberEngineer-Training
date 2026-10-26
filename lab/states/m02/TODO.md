# TODO: start state for M02 (Lab Build with Terraform)

Lab needs are numbered as in the module's lab_needs list. `+ [done]` lines are covered by files in this folder;
`- [live]` lines can only be confirmed on a live cluster or account; `- [lab-build]` lines are provided by the lab build (Terraform, images, Helm), not by start states.

+ [done] 1: Checks the AWS identity works (policy contents are checked only by the real build).
- [lab-build] 1: IAM policy for EC2, VPC, KMS, S3, Budgets, Route 53, load balancing, IAM and tagging plus the extra KMS actions (terraform/iam_installer.tf).
- [lab-build] 2: FIPS RHEL 9 bastion, openshift-install-fips on the bastion (terraform/bastion.tf).
+ [done] 3: Checks $HOME/pull-secret.json exists.
- [lab-build] 3: Supplying the pull secret to lab shell.
+ [done] 4: Checks exactly one public Route 53 hosted zone.
+ [done] 5: Checks ssh-keygen and GNU date; git user.name and user.email are not checked here (git is outside the allowed tool list for state scripts).
- [lab-build] 6: Terraform 1.17.0 and the Session Manager plugin are in the tools image (lab/image/versions.txt).
- [live] 7: AWS service quotas for the instance type, one Elastic IP and one NAT gateway (needs the real account).
- [lab-build] 8: Real budget amount and the sweeper (terraform/sweeper, variables.tf).
- [lab-build] 9: lab start exporting KMS_KEY_ARN and VPC_ID from Terraform outputs (labcli/terraform.py, terraform/outputs_lab.tf).

Open items from review (live test or decision):
- Terraform lab build under lab/terraform/ (not provided): instance type, root volume, AZ selection, subnet roles, budget amount and auto-destroy sweeper (review M02).
