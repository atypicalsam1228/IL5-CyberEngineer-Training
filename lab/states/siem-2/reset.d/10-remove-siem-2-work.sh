#!/usr/bin/env bash
# Removes what SIEM-2 steps 2, 4 and 5 create. Step 3 (loki-config) is put back by the start files.
set -euo pipefail
. "$(dirname "$0")/../../_common/lib.sh"
oc get clusterrolebinding -o json |
  jq -r '.items[] | select(.roleRef.name == "audit-log-reader") | select(any(.subjects[]?; .kind == "ServiceAccount" and .namespace == "siem" and (.name == "auditor" or .name == "ordinary-user"))) | .metadata.name' |
  while read -r name; do oc delete clusterrolebinding "$name" --ignore-not-found; done
oc delete serviceaccount auditor ordinary-user -n siem --ignore-not-found
if oc get clusterlogforwarder "$SIEM_FORWARDER_NAME" -n "$LOGGING_NAMESPACE" >/dev/null 2>&1 && forwarder_has_delivery_mode; then
  oc patch clusterlogforwarder "$SIEM_FORWARDER_NAME" -n "$LOGGING_NAMESPACE" --type json \
    -p '[{"op":"remove","path":"/spec/outputs/0/loki/tuning"}]'
fi
if [ -n "${GRAFANA_URL:-}" ]; then
  uid=$(grafana_get /api/folders | jq -r '.[] | select(.title == "siem-storage") | .uid')
  [ -z "$uid" ] || curl -s -o /dev/null -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -X DELETE "$GRAFANA_URL/api/folders/$uid"
fi
