#!/usr/bin/env bash
# Idempotent: Deployment demo-app in demo with a fixed version tag (not latest) and runAsNonRoot: true, so its
# pods pass the three M07 policies when they restart. An existing demo-app is checked, not replaced.
set -euo pipefail
. "$(dirname "$0")/../_common/lib.sh"
ensure_demo_app
image=$(oc get deployment demo-app -n demo -o jsonpath='{.spec.template.spec.containers[0].image}')
case "$image" in
  *:latest | *:) die "demo-app image $image has no fixed tag; the M07 policies would block its pods" ;;
  *@sha256:* | *:*) ;;
  *) die "demo-app image $image has no tag; the M07 policies would block its pods" ;;
esac
oc get deployment demo-app -n demo -o json | jq -e '.spec.template.spec.securityContext.runAsNonRoot == true' >/dev/null ||
  die "demo-app pods do not set runAsNonRoot: true; the M07 policies would block them"
