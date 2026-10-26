# IL5 lab infrastructure (Terraform)

Root module for one learner lab. `versions.tf`, `variables.tf` (first five variables), `main.tf`, `network.tf` and `outputs.tf` follow generators/content/m02.py. Network differs only in AZ selection (see below). Everything else is added by the lab build.

## Variables
Required: `lab_id`, `region`, `destroy_after` (YYYY-MM-DD), `alert_email`.
Optional: `budget_limit_usd` (default "25", placeholder; set the real limit), `cluster_name` (default first 14 chars of lab_id), `instance_type` (m6i.4xlarge, placeholder), `bastion_instance_type`, `bastion_ami_id`, `ocp_channel` (stable-4.22), `log_retention_days` (1, Object Lock Compliance), `log_archive_days`, `log_expire_days`, `backup_expire_days`, `enable_ssm_endpoints`.

## Outputs
M02: `kms_key_arn vpc_id public_subnet_id private_subnet_id extra_security_group_id`.
Added: `lab_id aws_region cluster_name availability_zone log_bucket backup_bucket artifacts_bucket bastion_instance_id installer_policy_arns state_bucket_hint`, and `lab_env` (map for LAB_ID, AWS_REGION, CLUSTER_NAME, VPC_ID, KMS_KEY_ARN, BACKUP_BUCKET plus LOG_BUCKET, ARTIFACTS_BUCKET, BASTION_ID).
`lab up`: `terraform output -json lab_env | jq -r 'to_entries[]|"export \(.key)=\(.value)"'`.

## How `lab up` uses it
1. Create the state KMS key (alias `<lab_id>-tfstate`, rotation on) and the S3 state bucket encrypted with it (SSE-KMS, M02 Step 1), then `terraform init -backend-config=bucket=... -backend-config=region=... -backend-config=kms_key_id=<key ARN>`. The bastion and installer roles do not use the state bucket or key.
2. `terraform apply` (TF_VAR_* from env). Export `lab_env`.
3. Render install-config.yaml (M02 Step 5), upload to `s3://$ARTIFACTS_BUCKET/install/install-config.yaml` (SSE-KMS). The bastion (FIPS RHEL 9, no inbound, no key pair, no public IP) reboots into FIPS mode on first boot, then `lab-install.service` picks the file up, deletes it from S3, and runs `openshift-install-fips create cluster`.
4. Stream output: `aws ssm start-session --target $BASTION_ID --document-name AWS-StartInteractiveCommand --parameters command="tail -n +1 -F /var/log/lab-install.log"`. Poll `install/status` (installing, complete, failed:N). kubeconfig is at `install/auth/kubeconfig`.
5. Teardown: put an object at `install/destroy`, wait for status `destroyed`, then `terraform destroy`.

## Design notes
- AZ: public and private subnets use the first AZ (sorted, non-opt-in) offering both `instance_type` and `bastion_instance_type`; a precondition fails with a clear message if none does.
- KMS: rotation on; key policy keeps account root, lets CloudWatch Logs use the key, and lets account principals use it only via EC2 and S3 (so installer-created cluster roles and OADP work). Add the OADP/CSI roles by name later to tighten.
- Installer IAM: Red Hat OCP 4.22 list for an existing VPC, split in three managed policies (6,144 char limit), KMS actions scoped to the lab key, attached to the bastion role. `iam:CreateServiceLinkedRole` is an addition not on Red Hat's list.
- Lab-exercise IAM (`iam_lab_exercise.tf`): a separate managed policy for the module exercises that call AWS from the lab shell (M04: EnableKeyRotation, DisableKeyRotation, GetKeyRotationStatus, DescribeKey on the lab key ARN; CreateKey plus Encrypt, Decrypt, DisableKey, ScheduleKeyDeletion for M04 Test 5's throwaway key; the EBS default-encryption EC2 calls; get/put bucket encryption on the backup bucket only). It is NOT attached to the bastion role. Reason: `lab shell` runs in a local container and receives the learner's own AWS credentials (AWS_PROFILE and related variables, see lab/labcli/environment.py), so the bastion role is never the lab shell's identity; putting these actions on the bastion would widen an installer-only role that needs none of them. Terraform cannot know the learner identity, so name it in `lab_exercise_user_names` / `lab_exercise_role_names`, or attach the `lab_exercise_policy_arn` output by hand. The installer policy is unchanged. Limits: the EC2 EBS-default actions do not support resource scoping (Region condition only, and they change the account default for that Region, so use a lab account). The throwaway key's ARN is unknown in advance, so its four actions are allowed on any key in the account and Region, with an explicit Deny of DisableKey and ScheduleKeyDeletion on the lab key.
- Buckets: log (Object Lock Compliance, versioning, SSE-KMS, Glacier, expiry), backup (no lock so Velero can expire), artifacts. Compliance-locked versions cannot be removed early: wait `log_retention_days` before destroying the log bucket.
- Sweeper: tags `LabId` and `AutoDestroyAfter` (provider default_tags and installer userTags). `sweeper/` is a separate once-per-account module: hourly Lambda that emails expired LabIds (read-only). `scripts/sweep.sh [--apply]` does the destroying (cluster first via the bastion marker, then `terraform destroy`). Dry run by default; `--apply` also needs `SWEEP_ACCOUNT_ID` set to the account id, and only touches labs that have a state bucket in that account.

## Cost notes (ESTIMATE, not measured)
About $18 per learner is an estimate, not a quote. Main drivers: the cluster instance, NAT gateway and its hourly charge, the RHEL bastion, three interface endpoints (hourly each), EBS, load balancers. Destroy when stopping for the day. Budget alerts email at 80 percent actual and 100 percent forecast.

## Not verified (no apply was run)
RHEL 9 AMI name filter (Red Hat owner 309956199498, `Hourly2-GP3`), SSM agent install on RHEL, oc/release.txt paths on mirror.openshift.com, `oc adm release extract --command=openshift-install-fips` on a FIPS host, IAM policy sizes, Budgets permissions for the identity running Terraform (not included here), provider ~> 6.0 chosen to match m02.py.

## Open items for module text
- siem_2.py uses BACKUP_BUCKET for the Object Lock bucket; m04/m12 use it for the OADP bucket. Terraform makes two buckets; siem_2 should read LOG_BUCKET.
- m04 expects key rotation off at `lab start m04`; Terraform turns it on (m04 start must switch it off, which is drift).
