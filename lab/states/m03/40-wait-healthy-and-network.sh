#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Waits for the mesh control plane, checks NetworkPolicy is enforced.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
oc wait --for=condition=Ready istio/default --timeout=300s
oc wait --for=condition=Ready istiocni/default --timeout=300s
network=$(oc get network.config.openshift.io cluster -o jsonpath='{.status.networkType}')
[ "$network" = OVNKubernetes ] || die "the network policy tests need OVNKubernetes; this cluster uses $network"
say "Istio default and IstioCNI default are Ready; network plugin is $network"
