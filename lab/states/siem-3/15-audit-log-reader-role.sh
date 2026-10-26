#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. ClusterRole audit-log-reader is lab-provided; created only if missing,
# so the auditor binding in the next file works. See siem-2/40-audit-log-reader-role.sh.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_audit_log_reader_role
