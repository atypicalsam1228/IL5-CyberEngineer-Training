#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. ClusterRole audit-log-reader is lab-provided together with the Loki endpoint
# that enforces it. It is created here only when missing, so SIEM-2 step 2 can bind it. The exact rule the
# Loki endpoint checks must be confirmed on a live cluster.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_audit_log_reader_role
