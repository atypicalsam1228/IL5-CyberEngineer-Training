#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. SIEM-3 end state needed so the alert exists when role binding
# demo-extra-admin is created by the next file: Mattermost contact point, default route, and the
# privilege-change rule, written exactly as SIEM-3 steps 1 and 2 write them. Each is created only if missing.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env GRAFANA_URL GRAFANA_USER GRAFANA_PASSWORD MM_WEBHOOK_URL

if ! grafana_get /api/v1/provisioning/contact-points | jq -e 'any(.[]?; .name == "mattermost")' >/dev/null; then
  grafana_send POST /api/v1/provisioning/contact-points \
    "$(jq -n --arg url "$MM_WEBHOOK_URL" '{name: "mattermost", type: "slack", settings: {url: $url}}')" >/dev/null
fi
grafana_send PUT /api/v1/provisioning/policies '{"receiver":"mattermost","group_by":["alertname"],"group_wait":"0s"}' >/dev/null

folder_uid=$(grafana_get /api/folders | jq -r '[.[] | select(.title == "siem-detect") | .uid] | first // empty')
if [ -z "$folder_uid" ]; then
  folder_uid=$(grafana_send POST /api/folders '{"title":"siem-detect"}' | jq -r .uid)
fi
loki_uid=$(grafana_get /api/datasources/name/Loki | jq -r '.uid // empty')
[ -n "$folder_uid" ] && [ -n "$loki_uid" ] || die "could not read the siem-detect folder or the Loki data source in Grafana"

if grafana_get /api/v1/provisioning/alert-rules | jq -e 'any(.[]?; .title == "privilege-change")' >/dev/null; then
  say "alert rule privilege-change already exists"
  exit 0
fi
expr='sum(count_over_time({log_type="audit"} | json | verb="create" | objectRef_resource=~"rolebindings|clusterrolebindings" [5m]))'
query=$(jq -n --arg ds "$loki_uid" --arg expr "$expr" '{refId:"A",datasourceUid:$ds,relativeTimeRange:{from:600,to:0},model:{refId:"A",expr:$expr,queryType:"instant",instant:true}}')
cond=$(jq -n '{refId:"B",datasourceUid:"-100",relativeTimeRange:{from:0,to:0},model:{refId:"B",type:"classic_conditions",datasource:{type:"__expr__",uid:"-100"},conditions:[{type:"query",query:{params:["A"]},reducer:{type:"last",params:[]},evaluator:{type:"gt",params:[0]},operator:{type:"and"}}]}}')
rule=$(jq -n --arg folder "$folder_uid" --argjson a "$query" --argjson b "$cond" \
  '{title:"privilege-change",ruleGroup:"detect",folderUID:$folder,noDataState:"OK",execErrState:"Error","for":"0s",condition:"B",labels:{control:"AU-6"},annotations:{summary:"privilege-change"},data:[$a,$b]}')
grafana_send POST /api/v1/provisioning/alert-rules "$rule" | jq -e '.uid' >/dev/null || die "Grafana refused the privilege-change rule"
