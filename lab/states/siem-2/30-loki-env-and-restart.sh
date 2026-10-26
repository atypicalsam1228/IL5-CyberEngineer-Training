#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Loki (deployment loki, namespace siem) is lab-provided. This sets the three
# variables SIEM-2 step 3 expands in the config and rolls Loki when the config map changed.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env LOG_BUCKET KMS_KEY_ARN AWS_REGION
oc get deployment loki -n siem >/dev/null || die "deployment loki is missing in namespace siem (lab build provides it)"
oc get deployment loki -n siem -o json | jq -e '[.spec.template.spec.containers[0].args[]?] | any(. == "-config.expand-env=true")' >/dev/null ||
  die "Loki must start with -config.expand-env=true (lab build)"
oc set env deployment/loki -n siem LOG_BUCKET="$LOG_BUCKET" KMS_KEY_ARN="$KMS_KEY_ARN" AWS_REGION="$AWS_REGION" >/dev/null
want=$(oc get configmap loki-config -n siem -o jsonpath='{.data.config\.yaml}' | cksum | cut -d' ' -f1)
have=$(oc get deployment loki -n siem -o jsonpath='{.spec.template.metadata.annotations.il5-lab/loki-config-sum}')
if [ "$want" != "$have" ]; then
  oc patch deployment loki -n siem --type merge \
    -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"il5-lab/loki-config-sum\":\"$want\"}}}}}" >/dev/null
fi
oc rollout status deployment/loki -n siem --timeout=240s
