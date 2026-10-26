#!/usr/bin/env bash
# NOT YET RUN ON A LIVE CLUSTER. Removes what M05 creates: the il5 realm (users, clients, flows go with it),
# the OpenShift side of the Keycloak sign-in, and the token inactivity setting.
set -euo pipefail
. "$(dirname "$0")/../../_common/lib.sh"
require_env KEYCLOAK_URL KEYCLOAK_ADMIN_USER KEYCLOAK_ADMIN_PASSWORD
ca=$(mktemp)
trap 'rm -f "$ca"' EXIT
oc get configmap default-ingress-cert -n openshift-config-managed -o jsonpath='{.data.ca-bundle\.crt}' >"$ca"
token=$(curl -s --cacert "$ca" -d client_id=admin-cli -d grant_type=password -d username="$KEYCLOAK_ADMIN_USER" \
  --data-urlencode password="$KEYCLOAK_ADMIN_PASSWORD" "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" | jq -r '.access_token // empty')
[ -n "$token" ] || die "no Keycloak admin token; cannot remove the il5 realm"
code=$(curl -s --cacert "$ca" -o /dev/null -w '%{http_code}' -X DELETE -H "Authorization: Bearer $token" "$KEYCLOAK_URL/admin/realms/il5")
case "$code" in 204 | 404) ;; *) die "Keycloak refused to delete realm il5 (HTTP $code)" ;; esac
if oc get oauth cluster -o json | jq -e 'any(.spec.identityProviders[]?; .name == "keycloak")' >/dev/null; then
  oc patch oauth cluster --type merge -p '{"spec":{"identityProviders":null,"tokenConfig":{"accessTokenInactivityTimeout":null}}}'
fi
oc delete secret keycloak-client-secret -n openshift-config --ignore-not-found
oc delete configmap keycloak-ca -n openshift-config --ignore-not-found
