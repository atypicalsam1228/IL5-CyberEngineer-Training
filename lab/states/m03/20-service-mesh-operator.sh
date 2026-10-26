#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Installs OpenShift Service Mesh 3 (package servicemeshoperator3).
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_operator servicemeshoperator3 openshift-operators global
wait_until "the Istio CRD" crd_established istios.sailoperator.io
wait_until "the IstioCNI CRD" crd_established istiocnis.sailoperator.io
