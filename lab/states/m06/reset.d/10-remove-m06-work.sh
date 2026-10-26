#!/usr/bin/env bash
# NOT YET RUN ON A LIVE ACCOUNT. Removes the RBAC M06 step 1 creates and the account-wide Session Manager
# documents M06 step 3 creates. It will not touch AWS while the jump host still exists: run
# 'terraform destroy' in your M06 working folder first (the jump host, its role and log group live in
# your Terraform state, and deleting around Terraform would leave it out of step).
set -euo pipefail
. "$(dirname "$0")/../../_common/lib.sh"
oc delete clusterrolebinding il5-platform-admin il5-auditor --ignore-not-found
oc delete clusterrole il5-platform-admin --ignore-not-found
oc delete rolebinding il5-developer -n demo --ignore-not-found
require_env AWS_REGION LAB_ID
running=$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=tag:Name,Values=jump-$LAB_ID" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'length(Reservations[].Instances[])' --output text)
[ "$running" = 0 ] || die "jump host jump-$LAB_ID still exists; run 'terraform destroy' in your M06 folder, then 'lab reset m06' again"
for doc in SSM-SessionManagerRunShell "il5-logged-command-$LAB_ID"; do
  if aws ssm describe-document --name "$doc" --region "$AWS_REGION" >/dev/null 2>&1; then
    aws ssm delete-document --name "$doc" --region "$AWS_REGION"
  fi
done
