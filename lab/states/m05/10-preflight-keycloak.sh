#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Read-only checks of what M05 assumes (Keycloak itself is lab-provided).
# It does not create the il5 realm, users, clients or flows: those are what M05 builds.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
require_env KEYCLOAK_URL KEYCLOAK_ADMIN_USER KEYCLOAK_ADMIN_PASSWORD
ca=$(mktemp)
trap 'rm -f "$ca"' EXIT
oc get configmap default-ingress-cert -n openshift-config-managed -o jsonpath='{.data.ca-bundle\.crt}' >"$ca"
[ -s "$ca" ] || die "configmap default-ingress-cert has no ca-bundle.crt"

token=$(curl -s --cacert "$ca" -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" \
  --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" | jq -r '.access_token // empty')
[ -n "$token" ] || die "Keycloak at $KEYCLOAK_URL did not give an admin token (is it up, and signed by the cluster ingress CA?)"

oc get secret card-ca -n keycloak -o json | jq -e '.data["tls.crt"] and .data["tls.key"]' >/dev/null ||
  die "secret card-ca (tls.crt and tls.key) is missing in namespace keycloak (lab build provides the card authority)"

realm_code=$(curl -s --cacert "$ca" -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $token" "$KEYCLOAK_URL/admin/realms/il5")
if [ "$realm_code" = 200 ]; then
  say "NOTE: realm il5 already exists. M05 step 1 creates it, so run 'lab reset m05' first."
fi
say "Keycloak answers over HTTPS with the cluster ingress CA, an admin token was issued, card-ca exists"
