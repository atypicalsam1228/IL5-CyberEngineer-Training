#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only: audit logs already reach Loki, and Loki accepts pushes
# (an empty push; nothing is stored).
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env LOKI_URL LOKI_CA_FILE LOKI_USER LOKI_PASSWORD
loki_get "$LOKI_URL/loki/api/v1/label/log_type/values" | jq -e '.data | index("audit") != null' >/dev/null ||
  die "no audit logs in Loki yet (SIEM-1 must be done and the forwarder running)"
code=$(loki_get -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"streams":[]}' "$LOKI_URL/loki/api/v1/push")
case "$code" in 2??) ;; *) die "Loki did not accept a push (HTTP $code)" ;; esac
say "audit logs reach Loki and the push address accepts writes"
