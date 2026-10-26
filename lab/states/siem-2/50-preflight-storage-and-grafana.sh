#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only: the log bucket and Grafana data sources are lab-provided.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env LOG_BUCKET AWS_REGION GRAFANA_URL GRAFANA_USER GRAFANA_PASSWORD
aws s3api get-object-lock-configuration --bucket "$LOG_BUCKET" --region "$AWS_REGION" |
  jq -e '.ObjectLockConfiguration.Rule.DefaultRetention.Mode == "COMPLIANCE"' >/dev/null ||
  die "bucket $LOG_BUCKET does not have a Compliance-mode default Object Lock retention"
aws s3api get-bucket-encryption --bucket "$LOG_BUCKET" --region "$AWS_REGION" |
  jq -e '.ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm == "aws:kms"' >/dev/null ||
  die "bucket $LOG_BUCKET is not encrypted with aws:kms"
aws s3api get-bucket-lifecycle-configuration --bucket "$LOG_BUCKET" --region "$AWS_REGION" |
  jq -e 'any(.Rules[]?.Transitions[]?; .StorageClass == "GLACIER")' >/dev/null ||
  die "bucket $LOG_BUCKET has no lifecycle transition to GLACIER"
for source in Loki Prometheus; do
  [ -n "$(grafana_get "/api/datasources/name/$source" | jq -r '.uid // empty')" ] || die "Grafana has no data source named $source"
done
say "log bucket is locked, encrypted and archived; Grafana has the Loki and Prometheus data sources"
