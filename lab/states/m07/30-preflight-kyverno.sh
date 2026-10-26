#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only: Kyverno (lab-provided) must be running in namespace kyverno.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
oc get namespace kyverno >/dev/null || die "namespace kyverno is missing (the lab build installs Kyverno)"
oc get crd clusterpolicies.kyverno.io >/dev/null || die "Kyverno ClusterPolicy CRD is missing"
ready=$(oc get pods -n kyverno -o json | jq '[.items[] | select(.status.phase == "Running")] | length')
[ "$ready" -ge 1 ] || die "no Kyverno pod is Running in namespace kyverno"
say "Kyverno is running ($ready pods)"
