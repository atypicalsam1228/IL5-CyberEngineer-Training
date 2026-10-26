#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only: Loki (lab-provided in namespace siem) must answer ready.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env LOKI_URL LOKI_CA_FILE LOKI_USER LOKI_PASSWORD
oc get namespace siem >/dev/null || die "namespace siem is missing (Loki, Grafana and Alloy are provided by the lab build)"
[ "$(loki_get "$LOKI_URL/ready")" = ready ] || die "Loki did not answer ready at $LOKI_URL"
say "Loki answers ready"
