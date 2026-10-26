#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. SIEM-2 end state for the forwarder: created if missing, with the delivery
# mode SIEM-2 step 5 adds. An existing forwarder is kept and only gets the delivery mode if it lacks it.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_siem_forwarder tuned
