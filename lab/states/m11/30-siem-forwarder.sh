#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. M11 needs SIEM-1 done (application logs reaching Loki). This creates the
# SIEM-1 end state only if it is missing; an existing forwarder is left as it is.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_siem_forwarder
