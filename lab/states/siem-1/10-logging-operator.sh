#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Installs the Red Hat OpenShift Logging operator (package cluster-logging)
# and waits for the collect-* cluster roles SIEM-1 step 2 binds. Creates NO collector, secret or forwarder.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_operator cluster-logging openshift-logging all
for role in collect-application-logs collect-infrastructure-logs collect-audit-logs; do
  wait_until "cluster role $role" oc get clusterrole "$role"
done
