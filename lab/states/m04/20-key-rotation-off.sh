#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Needs KMS_KEY_ARN and AWS_REGION from the lab.
set -euo pipefail
: "${KMS_KEY_ARN:?KMS_KEY_ARN is not set}"
aws kms disable-key-rotation --key-id "$KMS_KEY_ARN" --region "${AWS_REGION:?AWS_REGION is not set}"
