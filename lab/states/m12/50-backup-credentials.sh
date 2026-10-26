#!/usr/bin/env bash
# NOT YET RUN ON A LIVE ACCOUNT. Secret cloud-credentials (key cloud) in openshift-adp, for an IAM user that can
# read and write BACKUP_BUCKET and use KMS_KEY_ARN (generate data key, decrypt). Created only if the secret is
# missing. The IAM user is tagged LabId so the lab sweeper finds it. The key is never printed.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env BACKUP_BUCKET KMS_KEY_ARN AWS_REGION LAB_ID
if oc get secret cloud-credentials -n openshift-adp >/dev/null 2>&1; then
  say "secret cloud-credentials already exists"
  exit 0
fi
user="velero-$LAB_ID"
aws iam get-user --user-name "$user" >/dev/null 2>&1 ||
  aws iam create-user --user-name "$user" --tags "Key=LabId,Value=$LAB_ID" >/dev/null
policy=$(jq -n --arg b "arn:aws:s3:::$BACKUP_BUCKET" --arg k "$KMS_KEY_ARN" '{
  Version: "2012-10-17",
  Statement: [
    {Effect: "Allow", Action: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:AbortMultipartUpload", "s3:ListMultipartUploadParts"], Resource: ($b + "/*")},
    {Effect: "Allow", Action: ["s3:ListBucket", "s3:GetBucketLocation", "s3:ListBucketMultipartUploads"], Resource: $b},
    {Effect: "Allow", Action: ["kms:GenerateDataKey", "kms:Decrypt", "kms:DescribeKey"], Resource: $k}
  ]}')
aws iam put-user-policy --user-name "$user" --policy-name velero-backup --policy-document "$policy"
for key_id in $(aws iam list-access-keys --user-name "$user" --query 'AccessKeyMetadata[].AccessKeyId' --output text); do
  aws iam delete-access-key --user-name "$user" --access-key-id "$key_id"
done
credentials=$(aws iam create-access-key --user-name "$user" --output json |
  jq -r '"[default]\naws_access_key_id=" + .AccessKey.AccessKeyId + "\naws_secret_access_key=" + .AccessKey.SecretAccessKey')
oc create secret generic cloud-credentials -n openshift-adp --from-literal=cloud="$credentials" --dry-run=client -o yaml |
  oc apply -f - >/dev/null
