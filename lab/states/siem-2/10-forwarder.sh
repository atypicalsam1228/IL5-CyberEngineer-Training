#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. SIEM-1 end state: collector, secrets and siem-forwarder
# (created only if missing; the delivery-mode tuning is what SIEM-2 step 5 builds, so it is not added).
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_siem_forwarder
