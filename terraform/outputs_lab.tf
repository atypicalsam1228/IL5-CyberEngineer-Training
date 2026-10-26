# Outputs added beyond the five in outputs.tf (the M02 text). These feed the
# lab environment variables in LAB-CONTRACT.md. `lab up` reads lab_env as JSON.

output "lab_id" {
  value = var.lab_id
}

output "aws_region" {
  value = var.region
}

output "cluster_name" {
  value = local.cluster_name
}

output "availability_zone" {
  value = local.az
}

output "log_bucket" {
  description = "Object Lock (Compliance) log bucket for Loki (SIEM-2)."
  value       = aws_s3_bucket.log.id
}

output "backup_bucket" {
  description = "Backup bucket for OADP (M04, M12)."
  value       = aws_s3_bucket.backup.id
}

output "artifacts_bucket" {
  description = "Handoff bucket between the lab shell and the bastion."
  value       = aws_s3_bucket.artifacts.id
}

output "bastion_instance_id" {
  value = aws_instance.bastion.id
}

output "installer_policy_arns" {
  value = [for p in aws_iam_policy.installer : p.arn]
}

output "state_bucket_hint" {
  description = "Name of the Terraform state bucket the lab creates in M02 Step 1."
  value       = "${var.lab_id}-tfstate-${local.account_id}"
}

# Env var names from LAB-CONTRACT.md, ready to export.
# BACKUP_BUCKET follows M04/M12 (OADP). LOG_BUCKET is new: SIEM-2 text still
# says BACKUP_BUCKET for the Object Lock bucket (see README, open items).
output "lab_env" {
  value = {
    LAB_ID           = var.lab_id
    AWS_REGION       = var.region
    CLUSTER_NAME     = local.cluster_name
    VPC_ID           = aws_vpc.lab.id
    KMS_KEY_ARN      = aws_kms_key.lab.arn
    BACKUP_BUCKET    = aws_s3_bucket.backup.id
    LOG_BUCKET       = aws_s3_bucket.log.id
    ARTIFACTS_BUCKET = aws_s3_bucket.artifacts.id
    BASTION_ID       = aws_instance.bastion.id
  }
}
