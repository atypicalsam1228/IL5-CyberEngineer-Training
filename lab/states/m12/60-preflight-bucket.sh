#!/usr/bin/env bash
# NOT YET RUN ON A LIVE ACCOUNT. Read-only: the backup bucket exists and encrypts with KMS_KEY_ARN by default.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env BACKUP_BUCKET KMS_KEY_ARN AWS_REGION
aws s3api get-bucket-encryption --bucket "$BACKUP_BUCKET" --region "$AWS_REGION" |
  jq -e --arg k "$KMS_KEY_ARN" '.ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault | .SSEAlgorithm == "aws:kms" and .KMSMasterKeyID == $k' >/dev/null ||
  die "bucket $BACKUP_BUCKET is not encrypted by default with the lab KMS key"
say "bucket $BACKUP_BUCKET encrypts with the lab KMS key"
