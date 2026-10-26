#!/usr/bin/env bash
# Removes what SIEM-1 steps 2 and 3 create, so the learner can build it again.
set -euo pipefail
ns=openshift-logging
oc delete clusterlogforwarder siem-forwarder -n "$ns" --ignore-not-found
oc delete secret loki-credentials loki-ca -n "$ns" --ignore-not-found
oc get clusterrolebinding -o json |
  jq -r --arg ns "$ns" '.items[] | select(.roleRef.name | startswith("collect-")) | select(any(.subjects[]?; .kind == "ServiceAccount" and .name == "collector" and .namespace == $ns)) | .metadata.name' |
  while read -r name; do oc delete clusterrolebinding "$name" --ignore-not-found; done
oc delete serviceaccount collector -n "$ns" --ignore-not-found
