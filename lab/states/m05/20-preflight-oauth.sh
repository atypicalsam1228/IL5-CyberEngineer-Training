#!/usr/bin/env bash
# Read-only: M05 step 3 replaces the OAuth identity provider list, so no provider other than the one it
# creates (keycloak) may exist at the start. This does not delete anyone's provider.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
others=$(oc get oauth cluster -o json | jq -r '[.spec.identityProviders[]?.name | select(. != "keycloak")] | join(", ")')
[ -z "$others" ] || die "the OAuth resource already lists identity providers ($others); M05 step 3 would replace them"
if oc get oauth cluster -o json | jq -e 'any(.spec.identityProviders[]?; .name == "keycloak")' >/dev/null; then
  say "NOTE: the keycloak identity provider already exists. M05 step 3 creates it, so run 'lab reset m05' first."
fi
say "no other identity providers on the OAuth resource"
