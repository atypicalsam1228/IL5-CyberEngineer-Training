provider "aws" {
  region = var.region

  default_tags {
    tags = {
      LabId            = var.lab_id
      ManagedBy        = "terraform"
      AutoDestroyAfter = var.destroy_after
    }
  }

  ignore_tags {
    key_prefixes = ["kubernetes.io/"]
  }
}

resource "aws_kms_key" "lab" {
  description             = "Encrypts the ${var.lab_id} cluster root volume"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "lab" {
  name          = "alias/${var.lab_id}-lab"
  target_key_id = aws_kms_key.lab.key_id
}

resource "aws_budgets_budget" "lab" {
  name         = "${var.lab_id}-monthly"
  budget_type  = "COST"
  limit_amount = var.budget_limit_usd
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}
