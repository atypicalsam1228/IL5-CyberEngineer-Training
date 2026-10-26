#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only: Grafana data sources, the Mattermost webhook variable and
# Keycloak login events are lab-provided. The contact point and the rules are what SIEM-3 builds.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env GRAFANA_URL GRAFANA_USER GRAFANA_PASSWORD MM_WEBHOOK_URL KEYCLOAK_URL LOKI_URL LOKI_CA_FILE LOKI_USER LOKI_PASSWORD
for source in Loki Prometheus; do
  [ -n "$(grafana_get "/api/datasources/name/$source" | jq -r '.uid // empty')" ] || die "Grafana has no data source named $source"
done
oc get namespace keycloak >/dev/null || die "namespace keycloak is missing (lab build provides Keycloak)"
say "Grafana has the Loki and Prometheus data sources; MM_WEBHOOK_URL and KEYCLOAK_URL are set"
