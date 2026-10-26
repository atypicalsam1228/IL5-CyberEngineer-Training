#!/usr/bin/env bash
# Idempotent: service account auditor in siem, bound to ClusterRole audit-log-reader (created in SIEM-2).
set -euo pipefail
oc get clusterrole audit-log-reader >/dev/null || { echo "ClusterRole audit-log-reader is missing: finish SIEM-2 or have the lab provide it." >&2; exit 1; }
oc get namespace siem >/dev/null
oc create serviceaccount auditor -n siem --dry-run=client -o yaml | oc apply -f -
oc create clusterrolebinding auditor-audit-log-reader --clusterrole=audit-log-reader --serviceaccount=siem:auditor --dry-run=client -o yaml | oc apply -f -
