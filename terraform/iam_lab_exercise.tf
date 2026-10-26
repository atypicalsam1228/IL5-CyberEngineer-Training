# Permissions for the module exercises that call AWS directly from the lab shell
# (today: M04 key rotation, EBS default encryption, bucket encryption, and a
# throwaway key). This is separate from the installer policies on purpose: the
# installer policies belong to the bastion role and are Red Hat's published
# list; this policy belongs to the identity the learner's lab shell runs as.
#
# The lab shell does not use the bastion role. `lab shell` passes the learner's
# own AWS credentials (AWS_PROFILE, AWS_ACCESS_KEY_ID and so on) into the tools
# container, so Terraform cannot know that identity. Name it in
# lab_exercise_user_names or lab_exercise_role_names to attach the policy, or
# attach the policy ARN (output lab_exercise_policy_arn) by hand.

variable "lab_exercise_user_names" {
  type        = list(string)
  default     = []
  description = "IAM user names the learner's lab shell runs as. The lab-exercise policy is attached to each."
}

variable "lab_exercise_role_names" {
  type        = list(string)
  default     = []
  description = "IAM role names the learner's lab shell runs as. The lab-exercise policy is attached to each."
}

locals {
  # Any key in this account and Region. The throwaway key M04 Test 5 creates
  # has an ARN that is not known in advance; the tag condition does the scoping.
  any_key_arn         = "arn:aws:kms:${var.region}:${local.account_id}:key/*"
  throwaway_tag_value = "lab-exercise"
}

data "aws_iam_policy_document" "lab_exercise" {
  # Lab key only: describe, rotation on/off and status.
  statement {
    sid    = "LabKeyRotationAndDescribe"
    effect = "Allow"
    actions = [
      "kms:DescribeKey", "kms:EnableKeyRotation", "kms:DisableKeyRotation",
      "kms:GetKeyRotationStatus",
    ]
    resources = [aws_kms_key.lab.arn]
  }

  # M04 Test 5 creates a throwaway key tagged ManagedBy=lab-exercise, encrypts,
  # decrypts, disables it and schedules its deletion. CreateKey has no resource
  # scoping, so it is allowed only when the request carries that tag. Use,
  # disable and delete are allowed only on keys that already carry it, so the
  # learner identity cannot disable or delete any other key. TagResource is
  # allowed only to apply that exact tag value, and only to a key that has no
  # ManagedBy tag yet (it cannot re-tag a Terraform-managed key).
  statement {
    sid       = "ThrowawayKeyCreate"
    effect    = "Allow"
    actions   = ["kms:CreateKey"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/ManagedBy"
      values   = [local.throwaway_tag_value]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = [var.region]
    }
  }

  statement {
    sid       = "ThrowawayKeyTag"
    effect    = "Allow"
    actions   = ["kms:TagResource"]
    resources = [local.any_key_arn]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/ManagedBy"
      values   = [local.throwaway_tag_value]
    }

    condition {
      test     = "Null"
      variable = "aws:ResourceTag/ManagedBy"
      values   = ["true"]
    }
  }

  statement {
    sid       = "ThrowawayKeyUse"
    effect    = "Allow"
    actions   = ["kms:Encrypt", "kms:Decrypt", "kms:DisableKey", "kms:ScheduleKeyDeletion"]
    resources = [local.any_key_arn]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/ManagedBy"
      values   = [local.throwaway_tag_value]
    }
  }

  statement {
    sid       = "ProtectLabKeyFromDisableAndDeletion"
    effect    = "Deny"
    actions   = ["kms:DisableKey", "kms:ScheduleKeyDeletion"]
    resources = [aws_kms_key.lab.arn]
  }

  # Defense in depth: keys built by Terraform carry ManagedBy=terraform from the
  # provider default_tags, so they are denied even if a key were ever also given
  # the throwaway tag. The Allow above already limits disable and delete to keys
  # tagged ManagedBy=lab-exercise.
  statement {
    sid       = "ProtectTerraformManagedKeys"
    effect    = "Deny"
    actions   = ["kms:DisableKey", "kms:ScheduleKeyDeletion"]
    resources = [local.any_key_arn]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/ManagedBy"
      values   = ["terraform"]
    }
  }

  # EBS default encryption is an account-and-Region setting. These EC2 actions
  # do not support resource-level scoping, so "*" is required; the Region
  # condition is the only narrowing available. This changes the whole
  # account's default in this Region, so use a lab account.
  statement {
    sid    = "EbsDefaultEncryption"
    effect = "Allow"
    actions = [
      "ec2:EnableEbsEncryptionByDefault", "ec2:ModifyEbsDefaultKmsKeyId",
      "ec2:GetEbsEncryptionByDefault", "ec2:GetEbsDefaultKmsKeyId", "ec2:DescribeVolumes",
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = [var.region]
    }
  }

  # Bucket default encryption on the backup bucket only.
  statement {
    sid       = "BackupBucketEncryption"
    effect    = "Allow"
    actions   = ["s3:GetEncryptionConfiguration", "s3:PutEncryptionConfiguration"]
    resources = [aws_s3_bucket.backup.arn]
  }
}

resource "aws_iam_policy" "lab_exercise" {
  name        = "${var.lab_id}-lab-exercise"
  description = "Lab shell permissions for module exercises (M04 KMS and encryption) for lab ${var.lab_id}"
  policy      = data.aws_iam_policy_document.lab_exercise.json
}

resource "aws_iam_user_policy_attachment" "lab_exercise" {
  for_each   = toset(var.lab_exercise_user_names)
  user       = each.value
  policy_arn = aws_iam_policy.lab_exercise.arn
}

resource "aws_iam_role_policy_attachment" "lab_exercise" {
  for_each   = toset(var.lab_exercise_role_names)
  role       = each.value
  policy_arn = aws_iam_policy.lab_exercise.arn
}

output "lab_exercise_policy_arn" {
  description = "Attach this to the identity the lab shell runs as if you did not set lab_exercise_user_names or lab_exercise_role_names."
  value       = aws_iam_policy.lab_exercise.arn
}
