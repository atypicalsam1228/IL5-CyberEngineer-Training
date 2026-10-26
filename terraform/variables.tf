variable "lab_id" {
  type        = string
  description = "Short name of this lab. Used in names and tags."
}

variable "region" {
  type        = string
  description = "AWS region for every resource."
}

variable "destroy_after" {
  type        = string
  description = "Date (YYYY-MM-DD) after which this lab should be destroyed."

  validation {
    condition     = can(regex("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", var.destroy_after))
    error_message = "destroy_after must look like 2026-10-26."
  }
}

variable "alert_email" {
  type        = string
  description = "Address that receives budget alerts."
}

variable "budget_limit_usd" {
  type        = string
  default     = "25"
  description = "Monthly budget in US dollars. Placeholder; the lab sets the real amount."
}

# ---- Variables added beyond the M02 text (the lab build owns these) ----

variable "cluster_name" {
  type        = string
  default     = ""
  description = "OpenShift cluster name (CLUSTER_NAME). Empty means the first 14 characters of lab_id."

  validation {
    condition     = var.cluster_name == "" || can(regex("^[a-z][a-z0-9-]{0,13}$", var.cluster_name))
    error_message = "cluster_name must be 1 to 14 lowercase letters, digits or hyphens, starting with a letter."
  }
}

variable "instance_type" {
  type        = string
  default     = "m6i.4xlarge"
  description = "Single-node cluster instance type. Must match install-config.yaml. Placeholder size; confirm on a live lab."
}

variable "bastion_instance_type" {
  type        = string
  default     = "m6i.large"
  description = "Instance type of the FIPS-mode RHEL 9 bastion that runs openshift-install-fips."
}

variable "bastion_ami_id" {
  type        = string
  default     = ""
  description = "Override the RHEL 9 AMI. Empty means look up the latest Red Hat RHEL 9 AMI."
}

variable "ocp_channel" {
  type        = string
  default     = "stable-4.22"
  description = "Directory under mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp used to find oc and the release image."
}

variable "log_retention_days" {
  type        = number
  default     = 1
  description = "Default S3 Object Lock retention (Compliance mode) on the log bucket. Short on purpose so a lab can be destroyed."
}

variable "log_archive_days" {
  type        = number
  default     = 7
  description = "Days before log objects move to Glacier."
}

variable "log_expire_days" {
  type        = number
  default     = 14
  description = "Days before log object versions expire so the bucket can empty and be destroyed. Must exceed log_retention_days."
}

variable "backup_expire_days" {
  type        = number
  default     = 14
  description = "Days before backup bucket objects and old versions expire."
}

variable "enable_ssm_endpoints" {
  type        = bool
  default     = true
  description = "Create ssm, ssmmessages and ec2messages interface endpoints so Session Manager works privately (M06 needs this). Costs hourly per endpoint."
}
