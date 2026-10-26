#!/usr/bin/env bash
# NOT YET RUN ON A LIVE ACCOUNT. Read-only checks of what M06 step 3 (Terraform jump host) assumes.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env VPC_ID KMS_KEY_ARN AWS_REGION LAB_ID
command -v session-manager-plugin >/dev/null || die "the Session Manager plugin is not installed in lab shell"

services=$(aws ec2 describe-vpc-endpoints --region "$AWS_REGION" --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'VpcEndpoints[].ServiceName' --output json)
for name in ssm ssmmessages ec2messages; do
  printf '%s' "$services" | jq -e --arg s "com.amazonaws.$AWS_REGION.$name" 'index($s) != null' >/dev/null ||
    die "VPC $VPC_ID has no $name endpoint (the lab build creates them when enable_ssm_endpoints is true)"
done

aws kms get-key-policy --key-id "$KMS_KEY_ARN" --policy-name default --region "$AWS_REGION" --output text |
  jq -e 'any(.Statement[]?; (.Principal.Service // empty | tostring | test("^\\[?\"?logs\\.")))' >/dev/null ||
  die "the KMS key policy does not let CloudWatch Logs use the key"

if aws ssm describe-document --name SSM-SessionManagerRunShell --region "$AWS_REGION" >/dev/null 2>&1; then
  die "the Session Manager preferences document SSM-SessionManagerRunShell already exists; M06 step 3 creates it. Run 'lab reset m06'."
fi
say "Session Manager plugin, SSM endpoints, KMS policy for CloudWatch Logs are in place; no preferences document yet"
